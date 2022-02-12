from bs4 import BeautifulSoup
import requests

domains = {'서울': 'https://reading.ssem.or.kr',
           '부산': 'https://reading.pen.go.kr',
           '대구': 'https://reading.edunavi.kr',
           '인천': 'https://book.ice.go.kr',
           '광주': 'https://book.gen.go.kr',
           '대전': 'https://reading.edurang.net',
           '울산': 'https://reading.ulsanedu.kr',
           '세종': 'https://reading.sje.go.kr',
           '경기': 'https://reading.gglec.go.kr',
           '강원': 'https://reading.gweduone.net',
           '충북': 'https://reading.cbe.go.kr',
           '충남': 'https://reading.edus.or.kr',
           '전북': 'https://reading.jbedu.kr',
           '전남': 'https://reading.jnei.go.kr',
           '경북': 'https://reading.gyo6.net',
           '경남': 'https://reading.gne.go.kr',
           '제주': 'https://reading.jje.go.kr'}
url_find_school = "/r/newReading/search/schoolListData.jsp"
url_search_books = "/r/newReading/search/schoolSearchResult.jsp"
cookies = {
    'JSESSIONID': 'E7qMTypSehp1fshvYY4sNvIb3PcRZMGW3NztmOxZIdb5YQhE7rqV4ISd1akGe6IH.wasdls02_servlet_engine2',
    'D_VISITOR_ID': '600a7179-91ca-f930-422f-ddfff345e321',
}
headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}


def find_school(domain, school):
    resp = requests.post(domain + url_find_school, data={'schoolSearch': school}, cookies=cookies, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    school_list = soup.find_all(class_="school_name")
    if len(school_list) <= 1:
        return -1
    schoolCode = int((str(school_list[1])).split('schoolCode=')[1].split('&')[0])
    return schoolCode


def search_books(domain, schoolCode, query, option):
    options = {
        '전체': 'ALL',
        '자료명': 'TITL',
        '저자': 'AUTH',
        '출판사': 'PUBL',
        '주제': 'SUBJ',
        'ISBN': 'ISBN',
        'KDCN': 'KDCN'
    }
    option = options.get(option)
    if not option:
        return -1

    data = [
        ('schSchoolCode', str(schoolCode)),
        ('division1', option),
        ('searchCon1', query),
        ('connect1', 'A'),
        ('division2', 'TITL'),
        ('searchCon2', ''),
        ('connect2', 'A'),
        ('division3', 'PUBL'),
        ('searchCon3', ''),
        ('dataType', 'ALL'),
        ('lineSize', '40'),
        ('cbSort', 'STIT'),
    ]
    resp = requests.post(domain + url_search_books, data=data, cookies=cookies, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')

    images = []
    for i in soup.select("div.bd_list_no > div.book_image > img"):
        src = domain + i.attrs['src']
        if 'thumbNail' not in src:
            src = None
        images.append(src)
    titles = []
    for i in soup.select("div.bd_list_title > a > span"):
        titles.append(i.text)
    authors = []
    for i in soup.select("div.bd_list_info > div.bd_list_writer > span.dd"):
        authors.append(i.text.strip().replace("\r", "").replace("\n", "").replace("\t", ""))

    publishers = []
    years = []
    for i in soup.select("div.bd_list_info > div.bd_list_company > span.dd"):
        publishers.append(i.text.split('(')[0].strip())
        years.append(int(i.text.split('(')[1].split(')')[0]))
    KDCs = []
    for i in soup.select("div.bd_list_info > div.bd_list_year > span.dd"):
        KDCs.append(i.text.strip().replace("\r", "").replace("\n", "").replace("\t", ""))
    locations = []
    for i in soup.select("div.bd_list_info > div.bd_list_location > span.dd"):
        locations.append(i.text.replace("\r", "").replace("\n", "").replace("\t", ""))
    stats = []
    for i in soup.select("div.book_save > div "):
        stats.append(i.text.split('\n')[1])

    result = {
        "schoolName": soup.select_one("span.school_name").text,
        "schoolCode": schoolCode,
        "count": len(titles),
        "books": []
    }

    for i in range(0, len(titles)):
        info = {
            "title": titles[i],
            "author": authors[i],
            "publisher": publishers[i],
            "year": years[i],
            "KDC": KDCs[i],
            "location": locations[i],
            "stat": stats[i],
            "image": images[i]
        }
        result["books"].append(info)

    return result


print(search_books(domains.get("경기"), find_school(domains.get("경기"), "경기북"), "파이썬", "자료명"))
