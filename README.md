# 🔎 연동 시 세팅 방법 

1. requirements.txt 다운로드 <br>
  pip install -r requirements.txt

2. .env 환경 변수 설정, 키 json 파일 생성 <br>
   (노션 "키관리"참고)
   
3. 마이그레이션 적용 <br>
   python manage.py makemigrations <br>
   python manage.py migrate

4. 마이그레이션 오류 발생 시 db삭제 후 다시 명령어 입력

5. admin계정 생성 <br>
   python manage.py createsuperuser <br>
   -> 이름 : admin / 비밀번호 : admin 으로 통일 <br>
   -> 비밀번호 짧다는 질문 나오면 y로 무시 처리 <br>

6. 페르소나 계정 정보 DB에 적용 <br>
   python manage.py loaddata users/fixtures/users.json <br>

7. 가게 제보 키워드 리스트 DB에 적용 ➕ <br>
   python manage.py loaddata stores/fixtures/keywords.json <br> 

8. 서버 돌리기 <br>
   python manage.py runserver

9. 페르소나 계정 자동 로그인 버튼 눌렀을 때 로그인 되는지 확인 
    
10. 음성 인식 기능 잘 작동하는지 확인 (키가 제대로 들어갔는지 확인하는겁니다!)

11. 장바구니 AI 잘 작동하는지 확인 <br>
    예시 : 제육볶음에 들어가는 재료(돼지고기 등)를 파는 가게를 여러개 추가해놓고, 제육볶음을 검색했을 때 가게들이 나오는 지!
