DROP DATABASE IF EXISTS typeDB;

GRANT ALL PRIVILEGES ON *.* TO root@'%' IDENTIFIED BY 'qwerty' WITH GRANT OPTION;

CREATE DATABASE typeDB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;

USE typeDB;

CREATE TABLE sentences (
    id INT AUTO_INCREMENT PRIMARY KEY,  #고유 ID, 자동 증가, primary key
    sentence TEXT NOT NULL              #문장 (최대 글자수 제한 없음)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci; #한글 지원

INSERT INTO sentences (sentence) VALUES
('체다치즈를 최고 많이 먹은 최다연이 체다치즈 먹기 대회 최다 우승자이다.'),
('정희수가 희희낙락하게 희끄무리한 흰머리를 뽑으며'),
('이수지가 저수지에 갔는데 이 수지가 저수지에 간 걸까 저 수지가 저수지에 간걸까'),
('그 수지가 저수지에 간 걸까 하며 이수지는 고민했는데 고민 끝에 이수의 마이웨이를 부르며 불쾌지수가 올라가며'),
('저수지를 떠나 경기도 수지구의 한 학원으로 달려가더니 지수함수를 배워서 잘 사용하여 주식 수지를 맞아'),
('나 이수지, 바로 고단수지! 수지맞았다!하며 행복해했다.'),
('내가 그린 기린 그림은 잘 그린 기린 그림이고 네가 그린 기린 그림은 못 그린 기린 그림이다.'),
('내가 그린 기린 그림은 목이 긴 기린 그림이고, 네가 그린 기린 그림은 목이 안 긴 기린 그림이다'),
('내가 그린 구름그림은 새털구름 그린 구름그림이고, 네가 그린 구름그림은 깃털구름 그린 구름그림이다.'),
('저기 계신 저 분이 박 법학박사이시고 여기 계신 이 분이 백 법학박사이시다.'),
('김혜진, 류미성, 문채일 함께 만든 게임입니다. '),
('2024 클라우드 시스템 짱!');
