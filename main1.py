from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# DB 연결
conn = psycopg2.connect(
    host="localhost",
    dbname="postgres",
    user="postgres",
    password="@@lc717283"
)
cursor = conn.cursor()

# 입력 모델
class UserInput(BaseModel):
    gender: str
    age: str
    event: str
    time_sec: float | None = None  # 입력이 없을 수도 있으니 optional

@app.post("/predict_rank")
async def predict_rank(data: UserInput):
    # 상위 3명 기록
    query_top3 = """
        SELECT event, age, gender, meet, time, time_sec
        FROM swim_results
        WHERE gender = %s AND age = %s AND event = %s
        ORDER BY time_sec ASC
        LIMIT 3;
    """
    cursor.execute(query_top3, (data.gender, data.age, data.event))
    top3_results = cursor.fetchall()

    # 사용자 기록이 있는 경우 → 순위 예측
    if data.time_sec is not None:
        query_all = """
            SELECT time_sec
            FROM swim_results
            WHERE gender = %s AND age = %s AND event = %s
            ORDER BY time_sec ASC;
        """
        cursor.execute(query_all, (data.gender, data.age, data.event))
        times = [row[0] for row in cursor.fetchall()]

        rank = sum(1 for t in times if t < data.time_sec) + 1
        total = len(times)

        return {
            "user_rank": rank,
            "total_participants": total,
            "top3": [
                {
                    "event": row[0],
                    "age": row[1],
                    "gender": row[2],
                    "meet": row[3],
                    "time": row[4],
                    "time_sec": row[5],
                }
                for row in top3_results
            ]
        }
    else:
        # 사용자 기록 없으면 전체 기록만 보여줌
        return {
            "top3": [
                {
                    "event": row[0],
                    "age": row[1],
                    "gender": row[2],
                    "meet": row[3],
                    "time": row[4],
                    "time_sec": row[5],
                }
                for row in top3_results
            ]
        }
