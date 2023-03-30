from console import Console
from feedback import FGenerator
import httpx, json, names, random, secrets, time, tls_client, threading, os, multiprocessing

startt = time.time()
invoices = 1
feedbacks = 1

def rate(success, other):
    try:
        return (success / other) * 100
    except ZeroDivisionError:
        return 0
    
def calc_sex(counter):
    timer = time.time() - startt
    if timer >= 1:
        cps = counter / timer
        return f"{cps:.2f}"

def title_worker():
    while True:
        os.system(f"title Feedbacks: {feedbacks}, Success rate: {round(rate(feedbacks, invoices), 3)}%, Feedbacks Per Second: {calc_sex(feedbacks)} Time elapsed: {round(time.time() - startt, 3)}(s)")
        time.sleep(0.1)


class Feedback:
    def __init__(self):
        self.proxies: dict = {"http://": "http://169.197.82.58:16719", "https://": "http://169.197.82.58:16719"}
        self.client = httpx.Client(proxies=self.proxies)
        self.domains: list = ['fexbox.org', 'mailto.plus']
        self.config: dict = json.load(open("config.json"))
        self.shop: str = self.config.get("shop")
        self.reviews: str = FGenerator().generate_feedback()

    def _obtain_mail(self, mail, worker):
        try:
            resp = self.client.get(f'https://tempmail.plus/api/mails?email={mail}&limit=20&epin=', timeout=30)
            completed = resp.json()['first_id']
            if completed != 0:
                rep = self.client.get(f"https://tempmail.plus/api/mails/{completed}?email={mail}&epin=", timeout=30)
                feedback = rep.text.split(f"feedback: https://{self.shop}.mysellix.io/feedback/")[1].split(',')[0]
                Console("INFO").log(f"{worker} | Obtained Feedback Token: {feedback}")
                self._send_out(feedback, worker)
        except Exception as e:
            print(e)
            pass

    def _send_out(self, invoice_id, worker):
        global feedbacks
        try:
            Console("INFO2").log(f"{worker} | Attempting to send out feedback")
            headers = {"referer": f"https://{self.shop}.mysellix.io/feedback/{invoice_id}",
                       "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                     "like Gecko) Chrome/111.0.0.0 Safari/537.36"}
            quote = self.reviews.replace(".", "").replace("'", "").replace("!", "").lower()
            score = random.randint(4, 5)
            r = tls_client.Session(client_identifier="chrome108").post(
                f"https://{self.shop}.mysellix.io/api/shop/feedback/reply", proxy=self.proxies,
                json={"feedback": "positive", "message": quote, "score": score, "uniqid": invoice_id}, headers=headers)
            if r.json()['message'] == 'Feedback Sent Successfully.':
                Console("SUCCESS").log(f"{worker} | Sent Out Feedback Successfully | Score: {score}")
                feedbacks += 1
            else:
                Console("ERROR").log(f"{worker} | Failed To Send Out Feedback")
        except Exception as e:
            Console("ERROR").log(f"{worker} | Errored To Send Out Feedback")
            self._send_out(invoice_id, worker)

    def generate_invoice(self, worker):
        global invoices
        while True:
            email = f'{names.get_full_name().replace(" ", "")}{secrets.token_hex(4)}@{random.choice(self.domains)}'
            try:
                r = self.client.post("https://dev.sellix.io/v1/payments",
                                    headers={"Authorization": 'Bearer ' + self.config.get("sellix_auth")}, json={
                                        "title": "Title",
                                        "return_url": "http://1.1.1.1",
                                        "email": email,
                                        "currency": "USD",
                                        "description": "Test payment",
                                        "confirmations": 3,
                                        "credit_card": None,
                                        "product_id": self.config.get("product_id"),
                                        "quantity": 100000,
                                        "gateway": "SOLANA",
                                    }, timeout=30)
                uniqid = r.json()['data']['uniqid']
                r = self.client.put(f"https://dev.sellix.io/v1/payments/{uniqid}",
                            headers={"Authorization": 'Bearer ' + self.config.get("sellix_auth")}, timeout=30)
                if r.json()['message'] == "Payment Completed Successfully.":
                    Console("INFO").log(f"{worker} | Creating Invoice On Email: {email}")
                    invoices += 1
                    self._obtain_mail(email, worker)
                else:
                    pass
            except Exception as e:
                pass


if __name__ == '__main__':
    threading.Thread(target=title_worker).start()
    for _ in range(60):
        threading.Thread(target=Feedback().generate_invoice, args=[f"WORKER-{str(_+1)}"]).start()