# TCP통신으로 이미지 전송 후 분석하기

> 학교 과제(네트워크 프로그래밍)로 제출한 TCP통신을 하는 서버 + 클라이언트

꽃 이미지를 클라이언트에서 선택해서 서버로 보내면 서버가 분석해서 결과 보내줌

## 사용 라이브러리 + 버전

```
# python == 3.12

tensorflow==2.17.0
numpy==1.26.4
pandas==2.2.2
pillow==10.4.0
openpyxl==3.1.5
```

## 참고

당시 모델학습에 사용한 데이터는 kaggle에서 구했다

> Flower Classification with TPUs  
> https://www.kaggle.com/c/flower-classification-with-tpus/data

근데 막상 모델을 만들고 나니까 `accuracy`가 0.7밖에 안나왔는데, 당시에는 수정할 시간도 지식도 없어서 멀쩡하게 잘 분류되는 사진들만 학교에 가져가서 시연에 사용했다.
