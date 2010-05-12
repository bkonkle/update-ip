import unittest
from mock import Mock, sentinel, patch
from update_ip.services.base import BaseDNSService
from update_ip.updater import InvalidServiceError, IPUpdater

class TestIPUpdater(unittest.TestCase):
    
    def test_init(self):
        # Verify that IPUdater raises an InvalidService Error if an object
        # without a 'name' attribute (None) is passed to it upon init.
        self.assertRaises(InvalidServiceError, IPUpdater, None)
    
    @patch('__builtin__.open')
    def test_update_noargs_not_changed(self, mock_open):
        service = Mock(spec=BaseDNSService)
        updater = IPUpdater(service)
        updater.clear_stored_ip = Mock()
        updater.read_stored_ip = Mock()
        updater.read_stored_ip.return_value = '0.0.0.0'
        updater.get_public_ip = Mock()
        updater.get_public_ip.return_value = '0.0.0.0'
        updater.validate_ip = Mock()
        updater.status_update = Mock()
        updater.service.find_domains = Mock()
        updater.service.find_domains.return_value = 'testdomain.com'
        
        updater.update()
        
        # The clear_stored_ip method should only be called if clear=True is
        # passed to the update method.
        self.assertFalse(updater.clear_stored_ip.called)
        self.assertTrue(updater.read_stored_ip.called)
        # self.assertTrue(mock_open.called)
        self.assertTrue(updater.get_public_ip.called)
        self.assertTrue(updater.validate_ip.called)
        # Update should not be called, because the IP has not changed
        self.assertFalse(updater.service.update.called)

if __name__ == '__main__':
    unittest.main()
