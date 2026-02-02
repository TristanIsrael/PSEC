from safecor import SingletonMeta, Logger, RequestFactory, BenchmarkId
try:
    from safecor import InputsDaemon
except:
    print("DemonInputs not available")
from safecor import Mouse, MouseButton, ResponseFactory, FileHelper, MqttClient, Topics
import random, time

class ControleurBenchmark(metaclass=SingletonMeta):

    def setup(self, mqtt_client: MqttClient):
        self.mqtt_client = mqtt_client
        random.seed()

        #Logger().setup("Benchmark controller", mqtt_client)

    ###
    # Fonctions appelées par le DomU    
    #
    def demarre_benchmark_inputs(self):
        Logger().info("Demande le démarrage du benchmark sur les entrées", "BenchmarkController")
        payload = RequestFactory.create_request_start_benchmark(BenchmarkId.INPUTS)
        self.mqtt_client.publish("{}/request".format(Topics.BENCHMARK), payload)

    def demarre_benchmark_fichiers(self):
        Logger().info("Demande le démarrage du benchmark fichiers", "BenchmarkController")
        payload = RequestFactory.create_request_start_benchmark(BenchmarkId.FILES)
        self.mqtt_client.publish("{}/request".format(Topics.BENCHMARK), payload)

    ###
    # Fonctions exécutées sur sys-usb
    #
    def execute_benchmark_inputs(self):
        Logger().info("Exécution du benchmark sur les entrées", "BenchmarkController")

        start_ms = time.time()*1000

        iterations:int = Parametres().parametre(Cles.BENCHMARK_INPUTS_ITERATIONS)
        mouse = Mouse()
        for i in range(iterations):
            mouse.x = random.randrange(0, 1024, 1)
            mouse.y = random.randrange(0, 768, 1)
            mouse.buttons = random.choice([MouseButton.UNKNOWN, MouseButton.LEFT, MouseButton.MIDDLE, MouseButton.RIGHT])
            InputsDaemon().genere_evenement_souris(mouse)

        end_ms = time.time()*1000
        duration = int(end_ms-start_ms)
        response = ResponseFactory.create_reponse_benchmark_inputs(duration, iterations)
        self.mqtt_client.publish("{}/response".format(Topics.BENCHMARK), response)

    def execute_benchmark_fichiers(self):
        Logger().info("Exécution du benchmark sur les fichiers", "BenchmarkController")

        start_ms = time.time()*1000

        # Informe le demandeur que le benchmark vient de démarrer
        response = ResponseFactory.create_reponse_benchmark_fichiers_demarre()
        self.mqtt_client.publish("{}/response".format(Topics.BENCHMARK), response)

        # Le scénario de benchmark est le suivant :
        # prérequis - Vérification de la présence d'un support USB
        # Pour chaque taille de fichier
        #   1 - création d'un fichier sur le support USB
        #   2 - demande la lecture du fichier sur le support USB via API (calcul débit moyen)
        #   3 - demande la copie du fichier depuis le support USB vers le dépôt via API (calcul du débit moyen)
        #   4 - envoie une notification de modification du dépôt        
        
        # L'exécution du benchmark appelle des fonctions bloquantes.
        # La VM sys-usb sera bloquée pendant toute la durée du benchmark
        # Cela permet d'éviter d'être perturbé par des demandes sans rapport avec le benchmark
        liste_disques = FileHelper.get_disks_list()
        if len(liste_disques) == 0:
            Logger().error("The benchmark cannot start because no external storage is connected", "BenchmarkController")
            return #Fin 

        # On prend le premier disque disponible
        disque = liste_disques[0]
        Logger().info("Le benchmark sera exécuté sur le disque {}".format(disque), "BenchmarkController")

        # On crée une structure pour conserver les métriques
        metrics = []

        # Les tailles et quantité de fichiers sont :
        # | Taille | Quantité | Volume total (Mo) |
        # |---|---|---|
        # | 10 Ko | 100 | 1 Mo |
        # | 100 Ko | 100 | 10 Mo |
        # | 500 Ko | 100 | 50 Mo |
        # | 1 Mo | 10 | 10 Mo |
        # | 10 Mo | 10 | 100 Mo |
        # | 100 Mo | 10 | 1 Go |
        # | 500 Mo | 2 | 1 Go |
        # | 1 Go | 1 | 1 Go |
        self.__execute_benchmark_fichiers(disque= disque, taille_fichier_ko= 10, quantite_fichiers= 100, metrics= metrics)
        self.__execute_benchmark_fichiers(disque= disque, taille_fichier_ko= 100, quantite_fichiers= 100, metrics= metrics)
        self.__execute_benchmark_fichiers(disque= disque, taille_fichier_ko= 500, quantite_fichiers= 100, metrics= metrics)
        self.__execute_benchmark_fichiers(disque= disque, taille_fichier_ko= 1*1024, quantite_fichiers= 10, metrics= metrics)
        self.__execute_benchmark_fichiers(disque= disque, taille_fichier_ko= 10*1024, quantite_fichiers= 10, metrics= metrics)
        self.__execute_benchmark_fichiers(disque= disque, taille_fichier_ko= 100*1024, quantite_fichiers= 5, metrics= metrics)
        #self.__execute_benchmark_fichiers(disque= disque, taille_fichier_ko= 500*1024, quantite_fichiers= 2, emetteur= emetteur, metrics= metrics)
        #self.__execute_benchmark_fichiers(disque= disque, taille_fichier_ko= 1024*1024, quantite_fichiers= 1, emetteur= emetteur, metrics= metrics)

        # Informe le demandeur que le benchmark vient de se terminer
        response = ResponseFactory.create_reponse_benchmark_fichiers_termine(metrics)
        self.mqtt_client.publish("{}/response".format(Topics.BENCHMARK), response)
    
    def __execute_benchmark_fichiers(self, disque:str, taille_fichier_ko:int, quantite_fichiers:int, metrics:list):
        Logger().info("Démarrage d'une itération de benchmark fichier pour {} fichiers de {} Ko".format(quantite_fichiers, taille_fichier_ko), "BenchmarkController")

        point_montage = Parametres().parametre(Cles.CHEMIN_MONTAGE_USB)

        # Step 1 : create files on disk
        for n_fichier in range(1, quantite_fichiers+1):
            filepath = "{}/{}/benchfile_{}ko_{}".format(point_montage, disque, taille_fichier_ko, n_fichier)                        
            
            try:
                Logger().info("Etape 1 : Création du fichier {}".format(filepath), "BenchmarkController")
                start_ms = time.time()*1000
                FileHelper.create_file(filepath, taille_fichier_ko)
                end_ms = time.time()*1000
                metrics.append({"step": "write_on_disk", "size": taille_fichier_ko, "iteration": n_fichier, "duration_ms": end_ms-start_ms})                                
            except Exception as e:
                Logger().error("Error during file creation: {}".format(str(e)), "BenchmarkController")
                return
            
        # Step 2 : read files from disk
        for n_fichier in range(1, quantite_fichiers+1):
            filepath = "{}/{}/benchfile_{}ko_{}".format(point_montage, disque, taille_fichier_ko, n_fichier)
            Logger().info("Etape 2 : Lecture du fichier {}".format(filepath), "BenchmarkController")
            try:                
                start_ms = time.time()*1000
                
                file = open(filepath, "rb")
                while True:
                    chunk = file.read(1024)
                    if not chunk:
                        break

                end_ms = time.time()*1000
                metrics.append({"step": "read_from_disk", "size": taille_fichier_ko, "iteration": n_fichier, "duration_ms": end_ms-start_ms})                                
            except Exception as e:                
                Logger().error("Error during file read: {}".format(str(e)), "BenchmarkController")
                return

        # Step 3 : copy files to repository  
        for n_fichier in range(1, quantite_fichiers+1):
            filepath = "{}/{}/benchfile_{}ko_{}".format(point_montage, disque, taille_fichier_ko, n_fichier)
            fingerprint = ""
            Logger().info("Etape 2 : Copie du fichier dans le dépôt", "BenchmarkController")
            try:
                start_ms = time.time()*1000
                FileHelper.copy_file_to_repository(filepath, fingerprint)
                end_ms = time.time()*1000
                metrics.append({"step": "copy_to_repository", "size": taille_fichier_ko, "iteration": n_fichier, "duration_ms": end_ms-start_ms})                                
            except Exception as e:
                Logger().error("Error during copy to repository: {}".format(str(e)), "BenchmarkController")
                return
