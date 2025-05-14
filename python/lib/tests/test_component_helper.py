from psec import ComponentsHelper, Constantes, EtatComposant
import unittest

class TestComponentHelper(unittest.TestCase):    

    components = [
        { "id": Constantes.PSEC_DISK_CONTROLLER, "label": "System disk controller", "type": "core", "state": "unknown" },
        { "id": Constantes.PSEC_INPUT_CONTROLLER, "label": "Input controller", "type": "core", "state": "unknown" },
        { "id": Constantes.PSEC_IO_BENCHMARK, "label": "System I/O benchmark", "type": "core", "state": "unknown" }
    ]

    def setUp(self):        
        self.helper = ComponentsHelper()
        self.helper.update(self.components)

    def test_get_ids(self):   
        self.assertEqual(len(self.components), 3)
        self.assertEqual(len(self.helper.get_ids()), len(self.components))
        self.assertListEqual(self.helper.get_ids(), [Constantes.PSEC_DISK_CONTROLLER, Constantes.PSEC_INPUT_CONTROLLER, Constantes.PSEC_IO_BENCHMARK])        
        
    def test_get_states(self):
        states = self.helper.get_states()
        self.assertEqual(len(states), 3)
        self.assertEqual(states[Constantes.PSEC_DISK_CONTROLLER], EtatComposant.UNKNOWN)
        self.assertEqual(states[Constantes.PSEC_INPUT_CONTROLLER], EtatComposant.UNKNOWN)
        self.assertEqual(states[Constantes.PSEC_IO_BENCHMARK], EtatComposant.UNKNOWN)

    def test_update_state(self):
        components = [            
            { "id": Constantes.PSEC_INPUT_CONTROLLER, "label": "Input controller", "type": "core", "state": EtatComposant.READY },
            { "id": Constantes.PSEC_IO_BENCHMARK, "label": "System I/O benchmark", "type": "core", "state": EtatComposant.STARTING }
        ]

        self.helper.update(components)
        states = self.helper.get_states()
        self.assertEqual(len(states), 3)
        self.assertEqual(states[Constantes.PSEC_DISK_CONTROLLER], EtatComposant.UNKNOWN)
        self.assertEqual(states[Constantes.PSEC_INPUT_CONTROLLER], EtatComposant.READY)
        self.assertEqual(states[Constantes.PSEC_IO_BENCHMARK], EtatComposant.STARTING)

    def test_get_state(self):
        components = [            
            { "id": Constantes.PSEC_INPUT_CONTROLLER, "label": "Input controller", "type": "core", "state": EtatComposant.READY },
            { "id": Constantes.PSEC_IO_BENCHMARK, "label": "System I/O benchmark", "type": "core", "state": EtatComposant.STARTING }
        ]

        self.helper.update(components)
        self.assertEqual(self.helper.get_state(Constantes.PSEC_INPUT_CONTROLLER), EtatComposant.READY)

    def test_get_type(self):
        self.assertEqual(self.helper.get_type(Constantes.PSEC_DISK_CONTROLLER), "core")
        self.assertEqual(self.helper.get_type(Constantes.PSEC_INPUT_CONTROLLER), "core")
        self.assertEqual(self.helper.get_type(Constantes.PSEC_IO_BENCHMARK), "core")

    def test_get_by_type(self):
        ids = self.helper.get_ids_by_type("test")
        self.assertEqual(len(ids), 0)

        self.helper.update([  { "id": "test", "label": "Test 1", "type": "test", "state": EtatComposant.READY } ])
        ids = self.helper.get_ids_by_type("test")
        self.assertEqual(len(ids), 1)

if __name__ == "__main__":    
    unittest.main()