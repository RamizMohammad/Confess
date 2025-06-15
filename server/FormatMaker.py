import datetime

class formatMaker:
    def dateFormatMaker(iso_string: str) -> str:
        try:
            date = datetime.datetime.fromisoformat(iso_string)
            now = datetime.datetime.utcnow()
            delta = now - date

            if delta.days == 0:
                return "Today"
            elif delta.days == 1:
                return "Yesterday"
            elif delta.days < 7:
                return date.strftime("%A")
            elif delta.days < 30:
                return f"{delta.days // 7}w"
            elif delta.days < 365:
                return f"{delta.days // 30}m"
            else:
                return f"{delta.days // 365}y"
            
        except:
            return "Unknown"
        
    def countFormat(num: int) -> str:
        
        if num >= 1000000:
            return f"{num / 1000000:.1f}M"
        if num >= 1000:
            return f"{num / 1000:.1f}K"
        return str(num)