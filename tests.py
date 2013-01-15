import unittest
import traceback
from mock import Mock, sentinel, patch
import update_ip
from update_ip.services.base import BaseDNSService
from update_ip.updater import InvalidServiceError, UpdaterError, IPUpdater, State


class IPGettersTestCase(unittest.TestCase):
    def setUp(self):
        self.ip_getters= update_ip.updater.IP_GETTERS

    def test_get_ip_on_all_getters(self):
        ips=[]
        for getter in self.ip_getters:
            try:
                ips.append( getter.get_ip() )
            except Exception as e:
                traceback.print_exc( e )
                raise AssertionError("Could not get ip from "+str(getter))
        if not all( [ip==ips[0] for ip in ips] ):
            raise AssertionError("ips should be all equal: "+str(ips))

    
class IPUpdaterTestCase(unittest.TestCase):
    def setUp(self):
        self.ip_file = '/tmp/ip.txt'
        self.service = Mock(spec=BaseDNSService)
        self.service.find_domains=Mock( side_effect=NotImplementedError )
        self.updater = IPUpdater(self.service, self.ip_file)
        self.updater.state._getNewIp= Mock()
        self.updater.state._getNewIp.return_value = "1.1.1.1"
    
    def test_class_init(self):
        # Verify that IPUdater raises an InvalidService Error if an object
        # without a 'name' attribute (None) is passed to it upon init.
        self.assertRaises(InvalidServiceError, IPUpdater, None, self.ip_file)
    
    @patch('__builtin__.open')
    def test_update_not_changed(self, mock_open):
        self.updater.state.last_ip="1.1.1.1"
        self.updater.update(['testdomain.com'])
        # Update and open should not be called, because the IP has not changed
        self.assertFalse(self.updater.service.update.called)
        self.assertFalse(mock_open.called)
    
    @patch('__builtin__.open')
    def test_update_changed(self, mock_open):
        self.updater.state.last_ip="0.0.0.0"
        self.updater.update(['testdomain.com'])
        self.updater.service.update.assert_called_with('testdomain.com',
                                                       '1.1.1.1')
        mock_open.assert_called_with(self.ip_file, 'w')
    
    def test_update_no_ip_file_no_domains(self):        
        self.assertRaises(UpdaterError, self.updater.update)

if __name__ == '__main__':
    unittest.main()
