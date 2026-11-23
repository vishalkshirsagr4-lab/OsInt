import os,tempfile,unittest
class SmokeTests(unittest.TestCase):
 def test_schema(self):
  fd,path=tempfile.mkstemp();os.close(fd);old=os.environ.get("DB_PATH");os.environ["DB_PATH"]=path
  try:
   from database.initialization import init_db
   init_db()
   import sqlite3
   db=sqlite3.connect(path);tables={x[0] for x in db.execute("select name from sqlite_master where type='table'")};db.close()
   self.assertIn("users",tables);self.assertIn("daily_claims",tables)
  finally:
   if old is None:os.environ.pop("DB_PATH",None)
   else:os.environ["DB_PATH"]=old
   os.unlink(path)
if __name__=="__main__":unittest.main()
