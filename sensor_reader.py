from hdc302x import HDC302xRead
import json

def get_temp_hum():
    try:
        temp, hum = HDC302xRead()
        return json.dumps({"temperature": round(temp, 1), "humidity": round(hum, 1)})
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    print(get_temp_hum())
