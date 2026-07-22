import sys
import unittest

sys.path.insert(0, r'd:\Lorenzo\Smanettolon\Jarvis-Investor-Advisor\jarvis-investor-advisor')

suite = unittest.defaultTestLoader.discover('tests')
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
