from safecor import ComponentsHelper, Constants, ComponentState
import unittest

class TestComponentHelper(unittest.TestCase):

    components = [
        { "id": Constants.SAFECOR_DISK_CONTROLLER, "label": "System disk controller", "type": "core", "state": ComponentState.UNKNOWN },
        { "id": Constants.SAFECOR_INPUT_CONTROLLER, "label": "Input controller", "type": "core", "state": ComponentState.UNKNOWN },
        { "id": Constants.IO_BENCHMARK, "label": "System I/O benchmark", "type": "core", "state": ComponentState.UNKNOWN }
    ]

    udpate_components = [
        { "id": Constants.SAFECOR_INPUT_CONTROLLER, "label": "Input controller", "type": "core", "state": ComponentState.READY },
        { "id": Constants.IO_BENCHMARK, "label": "System I/O benchmark", "type": "core", "state": ComponentState.STARTING }
    ]

    def setUp(self):
        self.helper = ComponentsHelper()

    def test_get_ids(self):
        self.helper.clear()
        self.helper.update(self.components)
        self.assertEqual(len(self.components), 3)
        self.assertEqual(len(self.helper.get_ids()), len(self.components))
        self.assertListEqual(self.helper.get_ids(), [Constants.SAFECOR_DISK_CONTROLLER, Constants.SAFECOR_INPUT_CONTROLLER, Constants.IO_BENCHMARK])        
        
    def test_get_states(self):
        self.helper.clear()
        self.helper.update(self.components)
        states = self.helper.get_states()
        self.assertEqual(len(states), 3)
        self.assertEqual(states[Constants.SAFECOR_DISK_CONTROLLER], ComponentState.UNKNOWN)
        self.assertEqual(states[Constants.SAFECOR_INPUT_CONTROLLER], ComponentState.UNKNOWN)
        self.assertEqual(states[Constants.IO_BENCHMARK], ComponentState.UNKNOWN)

    def test_update_state(self):
        self.helper.clear()
        self.helper.update(self.components)
        self.helper.update(self.udpate_components)
        states = self.helper.get_states()
        self.assertEqual(len(states), 3)
        self.assertEqual(states[Constants.SAFECOR_DISK_CONTROLLER], ComponentState.UNKNOWN)
        self.assertEqual(states[Constants.SAFECOR_INPUT_CONTROLLER], ComponentState.READY)
        self.assertEqual(states[Constants.IO_BENCHMARK], ComponentState.STARTING)

    def test_get_state(self):
        self.helper.clear()
        self.helper.update(self.components)
        self.helper.update(self.udpate_components)
        self.assertEqual(self.helper.get_state(Constants.SAFECOR_INPUT_CONTROLLER), ComponentState.READY)

        self.assertEqual(self.helper.get_state("none"), ComponentState.UNKNOWN)

    def test_get_type(self):
        self.helper.clear()
        self.helper.update(self.components)
        self.helper.update(self.udpate_components)
        self.assertEqual(self.helper.get_type(Constants.SAFECOR_DISK_CONTROLLER), "core")
        self.assertEqual(self.helper.get_type(Constants.SAFECOR_INPUT_CONTROLLER), "core")
        self.assertEqual(self.helper.get_type(Constants.IO_BENCHMARK), "core")
        self.assertEqual(self.helper.get_type("none"), "")

    def test_get_by_type(self):
        self.helper.clear()
        self.helper.update(self.components)
        self.helper.update(self.udpate_components)
        ids = self.helper.get_ids_by_type("test")
        self.assertEqual(len(ids), 0)

        self.helper.update([  { "id": "test", "label": "Test 1", "type": "test", "state": ComponentState.READY } ])
        ids = self.helper.get_ids_by_type("test")
        self.assertEqual(len(ids), 1)

    def test_get_by_id(self):
        self.helper.clear()
        self.helper.update(self.components)
        self.helper.update(self.udpate_components)
        ids = self.helper.get_by_id("none")
        self.assertEqual(len(ids), 0)
        
        ids = self.helper.get_by_id(Constants.SAFECOR_DISK_CONTROLLER)
        self.assertEqual(len(ids), 4)

    def test_get_components(self):
        self.helper.clear()
        self.helper.update(self.components)
        self.assertEqual(self.helper.get_components(), self.components)

    def test_clear(self):
        self.helper.clear()
        self.helper.update(self.components)
        self.assertNotEqual(len(self.helper.get_components()), 0)
        self.helper.clear()
        self.assertEqual(len(self.helper.get_components()), 0)

if __name__ == "__main__":
    unittest.main()