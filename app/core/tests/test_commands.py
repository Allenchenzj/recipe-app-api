"""
Test Custom Django management commands
"""

#  patch is to mock the behaviour of the db
from unittest.mock import patch

# operationalerror is the common error that occurs when db is 
# not ready during connection
from psycopg2 import OperationalError as Psycopg2Error

# helper function in Django help us call a command by name
from django.core.management import call_command

# another exception might get thrown by db 
from django.db.utils import OperationalError

# for unit test, test the case where the db is not available
from django.test import SimpleTestCase

# patch is used for mocking the behaviour of db, for all different 
# test methods,base class has check method to check the status of 
# db, so mocking the check method to simulate the respnse
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands"""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready, 
            run the wait_for_db cmd and db already ready
            just continue with the execution of the application
        """
        # when check is called inside the test case, return true value
        patched_check.return_value =True
        call_command('wait_for_db')
        # make sure the wait_for_db method it's calling the right 
        # thing of default db
        patched_check.assert_called_once_with(databases=['default'])

    # mock the sleep between two db check, it correpsonds to 
    # 'patched_check argument' inside out
    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError. it is not ready yet"""
        # mocking work this way when wanting to raise exception, 
        # here want to raise the exception to tell the db not ready 
        # using side effect, it allows to pass in various items that
        # get handled differently depending on the type, this 
        # define various values happend each time in the order we 
        # call i first 2 times call the check method want the side 
        # effect raise Psycopg2Error error then raise 3 operational 
        # error, mean two stages of errors when connecting to db 
        # (not ready)
        patched_check.side_effect = [Psycopg2Error] * 3 + \
            [OperationalError] * 3 + [True]
        call_command('wait_for_db')
        self.assertEqual(patched_check.call_count, 7)
        # checking the wait_for_db calling check multiple times
        patched_check.assert_called_with(databases=['default'])