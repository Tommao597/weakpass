import httpx


async def detect_http_fingerprint(url: str):
    """HTTP应用指纹识别"""

    try:

        async with httpx.AsyncClient(timeout=5, verify=False) as client:

            r = await client.get(url)

            text = r.text.lower()
            headers = r.headers

            # WordPress
            if "wp-content" in text or "wordpress" in text:
                return "wordpress"

            # Tomcat
            if "apache tomcat" in text:
                return "tomcat"

            # Jenkins
            if "jenkins" in text:
                return "jenkins"

            server = headers.get("server", "").lower()

            if "nginx" in server:
                return "nginx"

            if "apache" in server:
                return "apache"

            return "http"

    except:
        return None