import unittest
from mock import Mock, sentinel, patch
from update_ip.services.base import BaseDNSService
from update_ip.updater import InvalidServiceError, InvalidIPError, IPUpdater

class IPUpdaterTestCase(unittest.TestCase):
    def setUp(self):
        self.ip_file = '/tmp/ip.txt'
        self.service = Mock(spec=BaseDNSService)
        self.service.find_domains = Mock()
        self.service.find_domains.return_value = ['testdomain.com']
        self.updater = IPUpdater(self.service, self.ip_file)

    def _mock_all_except(self, exclude_attrs):
        """
        Patches the updater methods with Mock objects, excluding the requested
        methods so that they will work properly in the test.
        """
        attrs = ['clear_stored_ip', 'read_stored_ip', 'get_public_ip',
                 'validate_ip', 'status_update', 'update']
        
        for exclude_attr in exclude_attrs:
            attrs.remove(exclude_attr)
        
        for attr in attrs:
            setattr(self.updater, attr, Mock())
    
    def test_class_init(self):
        # Verify that IPUdater raises an InvalidService Error if an object
        # without a 'name' attribute (None) is passed to it upon init.
        self.assertRaises(InvalidServiceError, IPUpdater, None, self.ip_file)
    
    @patch('__builtin__.open')
    def test_update_not_changed(self, mock_open):
        self._mock_all_except(['update'])
        self.updater.get_public_ip.return_value = '0.0.0.0'
        self.updater.read_stored_ip.return_value = '0.0.0.0'
        
        self.updater.update()
        
        # The clear_stored_ip method should only be called if clear=True is
        # passed to the update method.
        self.assertFalse(self.updater.clear_stored_ip.called)
        self.assertTrue(self.updater.read_stored_ip.called)
        self.assertTrue(self.updater.get_public_ip.called)
        self.assertTrue(self.updater.validate_ip.called)
        # Update and open should not be called, because the IP has not changed
        self.assertFalse(self.updater.service.update.called)
        self.assertFalse(mock_open.called)
    
    @patch('__builtin__.open')
    def test_update_changed(self, mock_open):
        self._mock_all_except(['update'])
        self.updater.get_public_ip.return_value = '0.0.0.0'
        self.updater.read_stored_ip.return_value = '1.1.1.1'
        
        self.updater.update()
        
        self.assertTrue(self.updater.read_stored_ip.called)
        self.assertTrue(self.updater.get_public_ip.called)
        self.assertTrue(self.updater.validate_ip.called)
        self.updater.service.update.assert_called_with('testdomain.com',
                                                       '0.0.0.0')
        mock_open.assert_called_with(self.ip_file, 'w')
    
    @patch('__builtin__.open')
    def test_update_custom_domains(self, mock_open):
        self._mock_all_except(['update'])
        self.updater.get_public_ip.return_value = '0.0.0.0'
        self.updater.read_stored_ip.return_value = '1.1.1.1'
        
        custom_domains = ['porkchopmilkshakeinyourmouth.com',
                         'usbchainsaw.com']
        self.updater.update(custom_domains)
        
        # Iterate over the set of arguments from each call
        for i, args in enumerate(self.updater.service.update.call_args_list):
            self.assertEqual(args, ((custom_domains[i], '0.0.0.0'), {}))
    
    @patch('__builtin__.open')
    def test_update_clear(self, mock_open):
        self._mock_all_except(['update'])
        self.updater.read_stored_ip.return_value = '1.1.1.1'
        self.updater.get_public_ip.return_value = '0.0.0.0'
        
        self.updater.update(clear=True)
        
        self.assertTrue(self.updater.clear_stored_ip.called)
    
    def test_update_invalid_address(self):
        self._mock_all_except(['update', 'validate_ip'])
        self.updater.get_public_ip.return_value = '1928.18362.12.1332'
        
        self.assertRaises(InvalidIPError, self.updater.update)
    
    def test_update_no_ip_file_no_domains(self):
        self._mock_all_except(['update'])
        self.updater.get_public_ip.return_value = '0.0.0.0'
        self.updater.read_stored_ip.return_value = None
        
        self.assertRaises(ValueError, self.updater.update)
    
    @patch('os.path.exists')
    @patch('__builtin__.open')
    def test_read_stored_ip(self, mock_open, mock_exists):
        self._mock_all_except(['read_stored_ip', 'validate_ip'])
        mock_exists.return_value = True
        mock_file = Mock()
        mock_file.read.return_value = '0.0.0.0.0'
        mock_open.return_value = mock_file
        
        self.assertRaises(InvalidIPError, self.updater.read_stored_ip)
        
        mock_file.read.return_value = '0.0.0.0'
        # Should not raise an error
        self.updater.read_stored_ip()

if __name__ == '__main__':
    unittest.main()
