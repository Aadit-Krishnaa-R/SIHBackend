# calls_model.py
calls_schema={
    
        "callid": int,
        "empid": int,
        "adminid": int,
        "coordinates": {
            "x": float,
            "y": float
        },
        "emotions": {
            "neutral":bool,
            "gratitude":bool,

            "happy": bool,
            "sad": bool,
            "anger": bool
        },
        "pos_percent": float,
        "neg_percent": float,
        "rating": int,
        "language": str,
        "duration": int
    
}