import sys, os, glob, py_compile, unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

print("=== py_compile ===")
files = glob.glob(os.path.join(ROOT, "**", "*.py"), recursive=True)
for f in files:
    py_compile.compile(f, doraise=True)
print("py_compile OK (%d files)" % len(files))

print("=== unittest ===")
loader = unittest.TestLoader()
suite = loader.discover(os.path.join(ROOT, "tests"))
runner = unittest.TextTestRunner(verbosity=2)
res = runner.run(suite)
sys.exit(0 if res.wasSuccessful() else 1)
