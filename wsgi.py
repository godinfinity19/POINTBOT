import sys
import os

# إضافة مسار المشروع
project_home = u'/home/fardousnashaat1/POINTBOT'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# تعيين المتغيرات البيئية
os.environ['DATABASE_URL'] = 'postgres://reward_db_6744_user:9JafL71tVDrsGmrjYa4hiRnHNhNWAoZW@dpg-cpoeicqj1k6c73a67klg-a.virginia-postgres.render.com/reward_db_6744'
os.environ['API_TOKEN'] = '7157789286:AAFVBQgNYHORN-q-R-RmjE8CHrf9aGAaH_s'
os.environ['PORT'] = '5000'

# استيراد التطبيق
from main import app as application
