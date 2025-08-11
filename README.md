# dukventure

# 초기 페르소나 계정 적용 방법

(admin 계정은 createsuperuser로 생성해주세요!)
1. 아래 명령어 터미널에 입력 - 초기 계정 데이터를 DB에 적용:
   python manage.py loaddata users/fixtures/users.json
2. .env 파일의 비밀번호로 로그인

- json 파일의 password는 암호화된 비밀번호이기 때문에 .env 파일의 password를 확인해주세요!
- 혹시 VS Code json 파일에서 한글이 깨져 보인다면 json 파일을 메모장으로 직접 열고, 다른 이름으로 저장 - 인코딩 방법을 UTF-8로 변경해서 덮어쓰기 해주세요!
   
