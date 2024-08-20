# TCP통신으로 이미지 전송 후 분석하기
> 2학년 2학기, 네트워크 프로그래밍 기말고사 제출 프로젝트

클라이언트에서 꽃 이미지를 서버로 보내면, 서버가 이미지를 분석하여 무슨 꽃인지에 대한 메시지를 생성하여 클라이언트에게 반환

## 기술 스택
- 언어 : `Python`

## 사용 라이브러리 + 버전
```
# python == 3.12

tensorflow==2.17.0
numpy==1.26.4
pandas==2.2.2
pillow==10.4.0
openpyxl==3.1.5
```

## 여담

당시 모델학습에 사용한 데이터는 kaggle에서 구했다

> Flower Classification with TPUs  
> https://www.kaggle.com/c/flower-classification-with-tpus/data
