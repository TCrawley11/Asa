import os
from supabase import create_client, Client

url: str = os.environ.get("https://zwckhjpazxympxcazifl.supabase.co")
# can use the key publicly as long as RLS is enabled
key: str = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp3Y2toanBhenh5bXB4Y2F6aWZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM0MDgxMTQsImV4cCI6MjA1ODk4NDExNH0.kBmd0wv0vzxcTDJbal-CE2iXrOKdj2nAVzyTq1wCwqY")

class SupabaseService:
    def __init__(self):
        self.supabase = supabase.create_client(url, key)
