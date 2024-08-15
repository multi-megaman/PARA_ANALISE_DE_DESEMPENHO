import threading
import requests
import json

# Example data to send in POST requests
cars_options = [
    {"plate": "ABC123", "description": """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut tristique, leo et accumsan interdum, felis eros molestie magna, nec tincidunt mauris diam varius mauris. Donec consectetur felis mauris, ut vulputate eros posuere at. Integer condimentum id tortor id auctor. Praesent sodales odio dolor, iaculis gravida eros sagittis at. Fusce vulputate, eros ut malesuada vulputate, mauris est posuere nunc, at imperdiet risus enim vitae massa. In id tristique leo. Proin placerat, risus in venenatis dignissim, lorem sapien gravida libero, at tempus ligula mi et turpis. Nam imperdiet fermentum diam ut ullamcorper. Cras rhoncus, ipsum ut euismod suscipit, purus est ullamcorper tellus, ac tincidunt lorem ex eleifend nunc. Maecenas luctus sodales nibh, quis auctor sapien ornare pharetra. Suspendisse vitae vestibulum augue, id lacinia leo. Curabitur mollis luctus lorem et rhoncus. Nulla facilisi. In tempor, nulla vel pulvinar finibus, urna enim dapibus ex, porta condimentum eros tellus id libero. Fusce fermentum sollicitudin pulvinar. Aenean aliquam ex sed tellus luctus, faucibus sollicitudin nulla mattis. Pellentesque dignissim, ex ac aliquam pretium, mi ex consectetur lacus, eu viverra urna eros suscipit nisi. Ut vel urna mi. Mauris condimentum, mauris nec cursus accumsan, sem urna ornare libero, ac euismod mauris ipsum vel mi. Duis porta vehicula vehicula. Vestibulum congue id arcu ac lobortis. Ut congue aliquam iaculis. Fusce consequat dignissim risus non finibus. Nam consectetur fermentum ex, eu semper dolor consectetur nec. Aliquam egestas sodales nisl, ut ultrices est finibus ultrices. Nulla consectetur quis nulla ut laoreet. Morbi lacinia pellentesque nisl, id fringilla metus porta eu. Sed facilisis elit sit amet magna efficitur, ac mattis justo tincidunt. Duis auctor nisi aliquet elit rhoncus consequat. Aenean congue erat felis, a commodo lectus ornare quis. Cras bibendum a nisl a dapibus. Vivamus commodo lacus orci, quis pellentesque velit rhoncus eu. Pellentesque eu tortor vel magna viverra tempus. Sed euismod, eros non hendrerit feugiat, turpis eros tempor magna, vitae maximus lectus leo eget elit. Ut sollicitudin lacus vitae dictum sodales. Praesent porta, lectus et interdum eleifend, libero ipsum luctus risus, nec pulvinar nunc lectus finibus lacus. Donec volutpat urna sapien, nec gravida turpis pharetra eget. Praesent urna enim, ultricies sit amet orci elementum, tempus gravida magna. Integer maximus pulvinar mauris, ut fermentum purus vestibulum eu. Praesent quis risus urna. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Mauris finibus massa at neque porta rhoncus. Mauris iaculis ex in ligula lobortis, quis pellentesque sem viverra. Sed vel semper eros, at mollis mauris. In quis sodales augue. Donec quis porta magna, ac sagittis eros. Aliquam ac vulputate orci, nec pretium nunc. Etiam at est consequat nulla blandit congue ac nec dui. Quisque fermentum elementum ullamcorper. Morbi a eros vitae erat tristique bibendum. Vestibulum dapibus, lectus ac tempus mattis, ex ante fermentum arcu, aliquet feugiat metus eros sit amet augue. Integer eu diam id velit malesuada mattis eu eget neque. Cras vitae erat sit amet augue bibendum ultricies feugiat id lorem. Curabitur sit amet porttitor odio. Mauris consequat facilisis ultricies. Curabitur id felis eu dui lobortis molestie at at risus. Sed nec ex sed orci tristique pretium a at lacus."""},
]

# The URL of the endpoint
url = "http://serverprojadsufrpe.ddns.net:5000/register"


def make_single_request(carID: int):
    response = requests.post(url, data=json.dumps(cars_options[carID]), headers={"Content-Type": "application/json"})
    try:
        response_data = response.json()
        # print(f"Status Code: {response.status_code}, Response: {response_data}")
    except json.decoder.JSONDecodeError:
        print(f"Status Code: {response.status_code}, Response could not be decoded as JSON.")

def make_request(carID: int, qnt):
    threads = []
    for _ in range(qnt):
        thread = threading.Thread(target=make_single_request, args=(carID,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    requests_qnt = 4000
    print("Starting to make requests to /register endpoint.")
    for i in range(len(cars_options)):
        make_request(i, requests_qnt)

print("Finished making requests to /register endpoint.")