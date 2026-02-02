from psec import ComponentsHelper, Constants, ComponentState
import unittest

class TestComponentHelper(unittest.TestCase):    

    components = [
        { "id": Constants.STR_PSEC_DISK_CONTROLLER, "label": "System disk controller", "type": "core", "state": "unknown" },
        { "id": Constants.STR_PSEC_INPUT_CONTROLLER, "label": "Input controller", "type": "core", "state": "unknown" },
        { "id": Constants.STR_IO_BENCHMARK, "label": "System I/O benchmark", "type": "core", "state": "unknown" }
    ]

    def setUp(self):        
        self.helper = ComponentsHelper()
        self.helper.update(self.components)

    def test_get_ids(self):   
        self.assertEqual(len(self.components), 3)
        self.assertEqual(len(self.helper.get_ids()), len(self.components))
        self.assertListEqual(self.helper.get_ids(), [Constants.STR_PSEC_DISK_CONTROLLER, Constants.STR_PSEC_INPUT_CONTROLLER, Constants.STR_IO_BENCHMARK])        
        
    def test_get_states(self):
        states = self.helper.get_states()
        self.assertEqual(len(states), 3)
        self.assertEqual(states[Constants.STR_PSEC_DISK_CONTROLLER], ComponentState.UNKNOWN)
        self.assertEqual(states[Constants.STR_PSEC_INPUT_CONTROLLER], ComponentState.UNKNOWN)
        self.assertEqual(states[Constants.STR_IO_BENCHMARK], ComponentState.UNKNOWN)

    def test_update_state(self):
        components = [            
            { "id": Constants.STR_PSEC_INPUT_CONTROLLER, "label": "Input controller", "type": "core", "state": ComponentState.READY },
            { "id": Constants.STR_IO_BENCHMARK, "label": "System I/O benchmark", "type": "core", "state": ComponentState.STARTING }
        ]

        self.helper.update(components)
        states = self.helper.get_states()
        self.assertEqual(len(states), 3)
        self.assertEqual(states[Constants.STR_PSEC_DISK_CONTROLLER], ComponentState.UNKNOWN)
        self.assertEqual(states[Constants.STR_PSEC_INPUT_CONTROLLER], ComponentState.READY)
        self.assertEqual(states[Constants.STR_IO_BENCHMARK], ComponentState.STARTING)

    def test_get_state(self):
        components = [            
            { "id": Constants.STR_PSEC_INPUT_CONTROLLER, "label": "Input controller", "type": "core", "state": ComponentState.READY },
            { "id": Constants.STR_IO_BENCHMARK, "label": "System I/O benchmark", "type": "core", "state": ComponentState.STARTING }
        ]

        self.helper.update(components)
        self.assertEqual(self.helper.get_state(Constants.STR_PSEC_INPUT_CONTROLLER), ComponentState.READY)

    def test_get_type(self):
        self.assertEqual(self.helper.get_type(Constants.STR_PSEC_DISK_CONTROLLER), "core")
        self.assertEqual(self.helper.get_type(Constants.STR_PSEC_INPUT_CONTROLLER), "core")
        self.assertEqual(self.helper.get_type(Constants.STR_IO_BENCHMARK), "core")

    def test_get_by_type(self):
        ids = self.helper.get_ids_by_type("test")
        self.assertEqual(len(ids), 0)

        self.helper.update([  { "id": "test", "label": "Test 1", "type": "test", "state": ComponentState.READY } ])
        ids = self.helper.get_ids_by_type("test")
        self.assertEqual(len(ids), 1)

if __name__ == "__main__":    
    unittest.main()