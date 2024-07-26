#!/usr/bin/env python
# coding: utf-8

# In[1]:


from ultralytics import YOLO
import cv2
import datetime
import os
import psycopg2
import socketio
import requests
from collections import defaultdict
from ultralytics.utils.checks import check_imshow, check_requirements
from ultralytics.utils.plotting import Annotator, colors
check_requirements("shapely>=2.0.0")
from shapely.geometry import Polygon, Point


# In[2]:


# PostegreSQL Bağlantısı
conn = psycopg2.connect(database = "Arabalar", 
                        user = "mithatcanbursali", 
                        host= 'localhost',
                        password = "sifre",
                        port = 5432)


# In[3]:


# SocketIO Client side tanımlaması
sio = socketio.Client()

# Bağlantı kontrol fonksiyonları
@sio.event
def connect():
    print('Connected to server')

@sio.event
def disconnect():
    print('Disconnected from server')

# 2110 portundaki Flask serverin'a socket ile bağlantı 
sio.connect('http://localhost:2110')


# In[4]:


# YoloV8N modelinin uygulamaya tanımlanması
model = YOLO("yolov8n.pt")


# In[5]:


# Obje sayma işlemini, PostegreSQL ve Flask sunucularına veri gönderimini sağlayan class

class ObjectCounter:

    def __init__(
        self,
        names,
        obj1_path_name,
        obj2_path_name,
        reg_name,
        reg_pts=[(350, 200), (800, 200), (800, 500), (350, 500)],
        count_reg_color=(255, 0, 255),
        count_txt_color=(0, 0, 0),
        count_bg_color=(255, 255, 255),
        line_thickness=2,
        view_img=False,
        view_counts=True,
        region_thickness=5,
    ):
        # Görüntülerin kayıt yolu
        self.obj1_path_name = obj1_path_name
        self.obj2_path_name = obj2_path_name
        
        # Sayımın gerçekleşeceği dikdörtgenin ismi, bölgesi, rengi ve kenar kalınlığının tanımlanması
        self.reg_name = reg_name
        self.reg_pts = reg_pts
        self.counting_region = None
        self.region_color = count_reg_color
        self.region_thickness = region_thickness
        
        # İşlenecek görüntünün ve video/sayacın görüntülenme parametreleri
        self.im0 = None
        self.tf = line_thickness
        self.view_img = view_img
        self.view_counts = view_counts
        
        # Objelerin tanımlandıktan sonra isimlerinin verilmesi, kenar çizgilerinin oluşturulması ve video isminin belirlenmesi
        self.names = names  
        self.annotator = None  
        self.window_name = "Obje Sayaci"
        
        # Bölgeden geçen objelerin sayısının tutulması, objelere göre ayrılması
        self.counts = 0
        self.count_ids = []
        self.class_wise_count = {}
        
        self.count_txt_color = count_txt_color
        self.count_bg_color = count_bg_color
        
        self.track_history = defaultdict(list) # Tespit edilen objelerin kaydının tutulması

        self.env_check = check_imshow(warn=True) # Video ortamının çalışıp çalışmadığının kontrol edilmesi
        
        self.counting_region = Polygon(self.reg_pts) # Dikdörtgenin tanımlanması

    # Objelerin takip edilmesi, dışarıya aktarılmasını sağlayan fonksiyon
    def extract_and_process_tracks(self, tracks):
        self.annotator = Annotator(self.im0, self.tf, self.names) # Tespit edilen objelerin video içerisinde görselize edilip etiketlendirilmesi
        self.annotator.draw_region(reg_pts=self.reg_pts, color=self.region_color, thickness=self.region_thickness) # Bölgenin video içerisinde görselize edilmesi
        
        # Modelin takip işleminin sağlanması/çalıştırılması
        if tracks[0].boxes.id is not None:
            boxes = tracks[0].boxes.xyxy.cpu()
            clss = tracks[0].boxes.cls.cpu().tolist()
            track_ids = tracks[0].boxes.id.int().cpu().tolist()
            
            # Etiketlendirilmenin gerçekleştirilmesi
            for box, track_id, cls in zip(boxes, track_ids, clss):
                self.annotator.box_label(box, label=f"{self.names[cls]}#{track_id}", color=colors(int(track_id), True))
                
                # Classlara bağlı olarak sayımların tanımlanması
                if self.names[cls] not in self.class_wise_count:
                    self.class_wise_count[self.names[cls]] = {"COUNT": 0}
                
                # Track geçmişinin geçici olarak tutulması
                track_line = self.track_history[track_id]
                track_line.append((float((box[0] + box[2]) / 2), float((box[1] + box[3]) / 2)))
                if len(track_line) > 30:
                    track_line.pop(0)
                
                
                prev_position = self.track_history[track_id][-2] if len(self.track_history[track_id]) > 1 else None # Bulunduğu konumun kontrolleri

                is_inside = self.counting_region.contains(Point(track_line[-1])) # Bölge içerisindeki kontrol
                
                # Bölge içerisine girildiğinde yapılacak işlemler
                if prev_position is not None and is_inside and track_id not in self.count_ids:
                    self.count_ids.append(track_id)
                    self.counts += 1 # Sayacın arttırılması
                    self.class_wise_count[self.names[cls]]["COUNT"] += 1 # Classlara göre sayacın arttırılması
                    currentdate = "{date:%Y-%m-%d_%H:%M:%S}".format(date=datetime.datetime.now()) # Güncel tarih/saat
                    
                    # 2=araba 5=otobus
                    
                    # Bölgeden geçen obje araba ise yapılacak işlemler
                    if cls == 2:
                        # Anlık görselin bilgisayar üzerine kaydedilmesi
                        os.chdir(self.obj1_path_name)
                        cv2.imwrite(f"{currentdate}.png", im0)
                        
                        # İstenilen bilgilerin PostegreSQL'e kaydedilmesi
                        cur = conn.cursor()
                        cur.execute(f"INSERT INTO image_datas(track_id, region_name, object_name, path_name, date_time) VALUES('{track_id}','{self.reg_name}','{self.names[cls]}','{self.obj1_path_name}','{currentdate}')");
                        conn.commit()
                        cur.close()
                    
                    # Bölgeden geçen obje otobüs ise yapılacak işlemler
                    elif cls == 5:
                        # Anlık görselin bilgisayar üzerine kaydedilmesi
                        os.chdir(self.obj2_path_name)
                        cv2.imwrite(f"{currentdate}.png", im0)
                        
                        # İstenilen bilgilerin soket ile Flask sunucusuna gönderilmesi
                        data = {
                        'track_id':track_id,
                        'region_name': self.reg_name,
                        'object_name': self.names[cls],
                        'path_name': self.obj2_path_name,
                        'date_time': currentdate,

                        }
                            
                        sio.emit('receive_data', data)
                                                                                                                       
                          
        labels_dict = {} # Sayacın görselizasyonunda sayıların objelere bağlı tutan yapı
        
        # İlgili objelere göre görselizasyonun güncellenmesi
        for key, value in self.class_wise_count.items():
            if value["COUNT"] != 0:
                if not self.view_counts:
                    continue
                else:
                    labels_dict[str.capitalize(key)] = f"{value['COUNT']} ADET"
                    
        # Sayacın görselizasyonunun gerçekleştirilmesi
        if labels_dict:
            self.annotator.display_analytics(self.im0, labels_dict, self.count_txt_color, self.count_bg_color, 10)
    
    # Videonun gösterilmesi
    def display_frames(self):
        if self.env_check:
            cv2.namedWindow(self.window_name)
            cv2.imshow(self.window_name, self.im0)
            
            # Q tuşu ile videodan çıkış
            if cv2.waitKey(1) & 0xFF == ord("q"):
                cap.release()
                cv2.destroyAllWindows()
                return
    
    # Obje sayacının başlaması
    def start_counting(self, im0, tracks):
        self.im0 = im0
        self.extract_and_process_tracks(tracks)
        if self.view_img:
            self.display_frames()
        return self.im0



# In[6]:


cap = cv2.VideoCapture("/Users/mithatcanbursali/Downloads/objectvideo.mp4") # Kaynak videonun açılması 
assert cap.isOpened(), "Video dosyasi okunurken hata olustu!"
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

# Görselizasyon için seçilen objelerin türkçeleştirilmesi
model_names = model.names
model_names.update({2: "araba"})
model_names.update({5: "otobus"})

# Class için objenin istenilen parametreler ile tanımlanması
counter = ObjectCounter(
    obj1_path_name="/Users/mithatcanbursali/Desktop/imageholder/araba",
    obj2_path_name="/Users/mithatcanbursali/Desktop/imageholder/otobus",
    reg_name="dikdortgen1",
    view_img=True,
    names=model_names,
)

# Objenin çağrılması ve video sonlandığında ilgili bağlantıların sonlanması
while cap.isOpened():
    success, im0 = cap.read()
    if not success:
        print("Video frame is empty or video processing has been successfully completed.")
        sio.disconnect()
        conn.close()
        break
    tracks = model.track(im0, persist=True, show=False, classes=[2,5])
    im0 = counter.start_counting(im0, tracks)


# In[ ]:





# In[ ]:




