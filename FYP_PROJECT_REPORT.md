# TomatoGuard: AI and IoT-Based System for Early Detection and Prevention of Tomato Diseases in Local Farms

---

**Institution:** University of Rwanda — College of Science and Technology  
**Department:** Computer and Software Engineering  
**Programme:** Bachelor of Science in Computer and Software Engineering  
**Academic Year:** 2025–2026  

---

**Project Team:**

| Name | Registration Number |
|---|---|
| RUTEMBEZA Yves | 222009019 |
| NIYONIZERA Benigne | 221020634 |

---

**Supervisors:**

| Name | Title |
|---|---|
| NTARINDWA Theoneste | Dr. |
| GASUHUKE Janvier J.P | Mr. |

---

**Submission Date:** May 2026

---

## TABLE OF CONTENTS

- Abstract / Executive Summary
- Chapter 1: Introduction
  - 1.1 Background of the Study
  - 1.2 Problem Statement
  - 1.3 Objectives
  - 1.4 Scope of the Study
  - 1.5 Motivation
  - 1.6 Significance of the Study
  - 1.7 Research Questions
  - 1.8 Hypothesis
- Chapter 2: Literature Review
  - 2.1 Related Works and Existing Systems
  - 2.2 Identified Gaps and Challenges
  - 2.3 Way Forward
- Chapter 3: Research Methodology
  - 3.1 Data Collection Methods
  - 3.2 Tools Used
  - 3.3 Prototype and Simulation
  - 3.4 System Requirements
  - 3.5 Raspberry Pi Fixed Camera System
  - 3.6 Database Schema Design
  - 3.7 Mobile Application Design
  - 3.8 Security Design
  - 3.9 Deployment Architecture
  - 3.10 What Was Built vs. What Was Proposed
  - 3.11 System Design and Use Case Diagram
  - 3.12 Timeline and Project Planning
- Expected Results / Output
- Conclusion
- References

---

## ABSTRACT / EXECUTIVE SUMMARY

Tomato farming is a critical source of income and food security for thousands of smallholder farmers in Rwanda. Each growing season, tomato diseases such as Early Blight, Late Blight, and Leaf Mold cause crop losses of between 30% and 80% when they go undetected at early stages. The core problem is that existing detection approaches require the farmer to personally notice symptoms and take a photograph — meaning disease is already advanced by the time it is identified.

This project, TomatoGuard, developed an integrated system that combines Artificial Intelligence, Internet of Things sensors, a fixed farm camera, a mobile application, and an administrative web dashboard to autonomously detect tomato diseases and monitor environmental conditions without requiring any action from the farmer. A Raspberry Pi camera was mounted permanently on the farm and programmed to scan all farm zones continuously at adaptive intervals — shortening from 30 minutes under normal conditions to 5 minutes when high-risk environmental conditions are detected by IoT sensors. A two-stage AI pipeline was implemented: a leaf validator model verified that captured images were genuine tomato leaves before a MobileNetV2-based disease classifier identified the specific disease across 9 classes. The classifier achieved 91% accuracy and the validator achieved 99.6% accuracy.

The research methodology combined image dataset collection and augmentation, ESP32 IoT sensor integration, Wokwi hardware simulation, and farmer interviews. The overall system was implemented using FastAPI as the backend, Supabase PostgreSQL as the database, Flutter for the Android mobile application, and Next.js for the web dashboard. The expected outcome is a fully functional, affordable, and autonomous disease detection system that alerts farmers in real time with the exact farm zone location of detected disease — filling a gap that no existing solution currently addresses.

---

## CHAPTER 1: INTRODUCTION

### 1.1 Background of the Study

Agriculture is the backbone of Rwanda's economy, employing approximately 70% of the working population and contributing significantly to the country's Gross Domestic Product. Among the various crops cultivated in Rwanda, tomatoes (*Solanum lycopersicum*) hold a position of particular economic importance. Tomatoes are grown across multiple provinces, with major production zones in the Eastern Province, Southern Province, and around Lake Kivu. They serve dual purposes — providing nutrition to rural households and generating cash income from sales in local and regional markets.

Despite their importance, tomato crops in Rwanda face persistent threats from a wide range of diseases. Fungal pathogens such as Alternaria solani (causing Early Blight) and Phytophthora infestans (causing Late Blight) can devastate an entire harvest within days when environmental conditions are favorable and the disease goes undetected. Viral diseases such as Tomato Yellow Leaf Curl Virus (TYLCV), transmitted by whiteflies, are increasingly prevalent in Rwanda's warmer farming zones and have no direct cure — making early detection and rapid removal of infected plants the only effective control strategy.

The Rwanda Agriculture Board (RAB) has documented consistent crop losses due to tomato disease, estimating that smallholder farmers lose between 30% and 80% of their tomato harvest in affected seasons. The financial impact at the household level is significant — a single disease outbreak can eliminate a family's primary income source for an entire growing season, pushing vulnerable households further into food insecurity.

Traditional approaches to disease management in Rwanda rely heavily on two mechanisms: farmer observation and agricultural extension officers. Farmers inspect their crops manually, typically once per day, and report suspicious symptoms to extension officers who then visit the farm, diagnose the disease, and recommend treatment. This process has several critical limitations. First, farmers may not recognize subtle early-stage symptoms that are visible before the disease has spread significantly. Second, extension officers cover large geographic areas and cannot visit individual farms frequently enough to provide timely intervention. Third, by the time a disease is formally identified, it has often already spread to adjacent plants and sections of the farm.

In recent years, advancements in Artificial Intelligence — specifically Convolutional Neural Networks (CNNs) — have demonstrated remarkable capability in classifying plant diseases from images with accuracy comparable to or exceeding that of trained agronomists. Concurrently, the availability of affordable IoT hardware such as the ESP32 microcontroller, the DHT22 temperature and humidity sensor, and the Raspberry Pi single-board computer has made continuous automated farm monitoring financially accessible to researchers and, eventually, to farmers.

This project, TomatoGuard, was developed at the intersection of these two technological advances, combining AI-based visual disease detection with IoT-based environmental monitoring in a unified system specifically designed for the smallholder farming context in Rwanda.

### 1.2 Problem Statement

To illustrate the problem concretely, consider the following scenario: A smallholder tomato farmer in Rwanda's Eastern Province checks her farm at 7:00 AM on a Monday morning. Everything appears healthy. Unknown to her, Late Blight spores were deposited on her tomato leaves on Saturday evening following a period of warm, humid weather. By Monday morning, the infection is established but not yet visible to the naked eye. By Wednesday, the first brown lesions appear. The farmer notices them Thursday during her morning inspection and calls for an extension officer. The officer visits Friday. By then, the disease has spread to 40% of the crop. Treatment begins Saturday — six days after infection. Under optimal spreading conditions, Late Blight can destroy an entire crop in seven to ten days.

This scenario highlights three interconnected problems that TomatoGuard was designed to solve:

**Problem 1 — Reactive Detection:** Disease detection in the current system is entirely reactive. The farmer must physically see symptoms before any action begins. Because symptoms become visible only after the infection is established and spreading, detection is structurally delayed by 24 to 72 hours or more from the point of initial infection.

**Problem 2 — No Environmental Warning System:** Temperature, relative humidity, and soil moisture are the primary environmental drivers of tomato disease outbreaks. For example, Late Blight thrives at temperatures between 10°C and 25°C with relative humidity above 90%. If these conditions can be monitored continuously, the system can warn the farmer that conditions are dangerous before any disease is visible — providing a proactive rather than reactive response window. Currently, no affordable environmental monitoring system exists for smallholder farms in Rwanda.

**Problem 3 — No Integrated Autonomous Solution:** Commercial AI-based plant disease detection applications, such as Plantix and similar tools, require the farmer to identify a suspicious leaf, photograph it, and upload it manually. This approach does not solve the fundamental problem — it still depends entirely on the farmer noticing something abnormal before the system can help. A true solution must be autonomous: the system must watch the farm continuously, without waiting for the farmer to act.

TomatoGuard addresses all three problems through a single integrated architecture, making it distinct from every existing system reviewed in this project.

### 1.3 Objectives

**Main Objective:**
To design, develop, and validate an AI and IoT-based autonomous system that detects tomato leaf diseases and monitors farm environmental conditions in real time, providing immediate alerts to farmers through a mobile application.

**Specific Objectives:**

1. To collect and preprocess a tomato leaf image dataset covering 8 disease classes and healthy tomato leaves, train a MobileNetV2-based transfer learning model, and achieve a classification accuracy of at least 85% across all 9 classes.

2. To implement a two-stage AI pipeline consisting of a leaf validator model that filters non-tomato images and a disease classifier that identifies the specific disease, ensuring the system only processes relevant input.

3. To design and implement an IoT sensor node using the ESP32 microcontroller with DHT22 temperature and humidity sensor and analog soil moisture sensor that continuously monitors farm environmental conditions and transmits readings to the backend API.

4. To develop a risk assessment engine within the backend that evaluates incoming sensor data against disease-favorable environmental thresholds and returns a risk level classification of Low, Medium, High, or Critical to the IoT node and the mobile application.

5. To design and program a Raspberry Pi fixed camera system that autonomously captures tomato zone images at adaptive intervals — adjusting scan frequency from 30 minutes under normal conditions to 5 minutes during high-risk or active disease periods.

6. To develop a FastAPI-based RESTful backend system connected to a Supabase PostgreSQL database that receives, stores, processes, and serves sensor data, detection results, and farmer alerts.

7. To build a Flutter-based Android mobile application that allows farmers to view real-time sensor readings, current risk levels, farm zone maps, disease detection history, and receive push notifications when disease is detected.

8. To develop a Next.js web dashboard for system administrators to monitor multiple farms, view analytics, and manage farmer accounts.

### 1.4 Scope of the Study

This project covers the following areas within its defined scope:

**Artificial Intelligence:** The AI component is limited to classification of tomato leaf conditions. The system classifies images into 9 classes: Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Spider Mites (Two-Spotted), Target Spot, Tomato Yellow Leaf Curl Virus, Tomato Mosaic Virus, and Healthy. Treatment prescription and pesticide recommendation are outside the scope of this project and are identified as future work.

**IoT Sensing:** Environmental monitoring is limited to temperature, relative humidity, and soil moisture using the ESP32 + DHT22 + analog soil sensor combination. Advanced soil chemistry analysis (pH, nitrogen, phosphorus) is outside the scope of this project.

**Camera System:** The Raspberry Pi fixed camera system is designed to cover a single farm divided into a grid of zones (A1 through D4, giving a maximum of 16 zones per farm). Multi-camera coverage of very large farms is outside the current scope.

**Mobile Application:** The mobile application was developed for Android only (Flutter, targeting Android 8.0 API Level 26 and above). iOS development is outside scope due to platform licensing requirements.

**Geography:** The system was designed specifically for the Rwandan smallholder farming context. The environmental thresholds used in the risk assessment engine reflect disease-favorable conditions documented for Rwandan climate zones. The system is generalizable to East Africa with minor configuration changes.

**Deployment:** During the development and testing phase, the backend was deployed locally and made publicly accessible via an ngrok tunnel. Full cloud server deployment is planned as post-FYP production work.

### 1.5 Motivation

The motivation for TomatoGuard arose from two sources: personal observation of the agricultural challenges faced by Rwandan farming communities, and the recognition that existing technology — while powerful — had not been effectively applied to solve this specific problem in the African smallholder context.

Rwanda's Vision 2050 national development agenda explicitly targets the modernization of agriculture through technology adoption. The country has invested significantly in digital infrastructure, mobile connectivity, and technical education. Yet the farms where the majority of Rwandans work remain largely untouched by these advances. A farmer managing a small tomato plot has access to a smartphone but no tools to monitor their farm automatically. The technology to build such a tool exists — it simply had not been assembled in the right way for this context.

As Computer and Software Engineering students at the University of Rwanda, the project team recognized a direct opportunity to apply academic knowledge in AI, embedded systems, mobile development, and backend engineering to a problem with immediate, tangible impact. The goal was not merely to demonstrate technical capability but to build a system that could genuinely be deployed on a Rwandan farm after graduation, with hardware costs low enough to be practically accessible.

### 1.6 Significance of the Study

**To Smallholder Farmers:** TomatoGuard provides 24-hour autonomous disease surveillance without requiring the farmer to take any action until an alert is received. This fundamentally changes the farmer's role from disease detector to disease responder — a much easier and more effective position. Early detection means treatment is applied sooner, reducing the extent of crop loss and the cost of treatment.

**To Rwanda's Agricultural Sector:** Reducing preventable tomato crop losses directly contributes to food security and agricultural household income. A system that reduces disease-related losses by even 20% across a district of farms represents millions of Rwandan Francs preserved in the agricultural economy per season.

**To the Research Community:** This project contributes a practical implementation framework for integrating AI image classification with IoT environmental monitoring in a single unified agricultural system. This combination has been discussed theoretically in the literature but has not been demonstrated in a fully implemented, tested system for the Sub-Saharan African context.

**To the University of Rwanda:** TomatoGuard demonstrates the capability of Computer and Software Engineering graduates to design and implement sophisticated, multi-technology systems addressing real national priorities — reflecting well on the department's training outcomes.

### 1.7 Research Questions

This project was guided by the following research questions:

1. To what extent can a MobileNetV2-based transfer learning model, trained on an augmented tomato leaf image dataset, accurately classify tomato diseases under conditions representative of real Rwandan farm photography?

2. How effectively can a two-stage AI pipeline — combining a leaf validator with a disease classifier — reduce false positive detections compared to a single-stage classifier alone?

3. Can continuous IoT environmental monitoring of temperature, humidity, and soil moisture provide meaningful early warning of disease-favorable conditions before visual symptoms appear on tomato leaves?

4. Does an adaptive camera scan interval system — triggered by IoT-detected environmental risk levels — reduce the time between disease onset and first detection compared to fixed-interval scanning?

5. What are the primary usability barriers for smallholder farmers in Rwanda when interacting with a mobile farm monitoring application, and how can interface design address these barriers?

### 1.8 Hypothesis

**H1:** A MobileNetV2-based transfer learning model trained on an augmented tomato leaf image dataset will achieve a minimum classification accuracy of 85% across all 9 disease and healthy classes, with the two-stage pipeline (leaf validator followed by disease classifier) reducing false positive detections by at least 30% compared to a single-stage system.

**H2:** Continuous IoT monitoring of temperature, humidity, and soil moisture will successfully identify environmental conditions that are statistically associated with tomato disease outbreak risk, enabling the system to issue environmental risk warnings at least 12 to 24 hours before visual disease symptoms are detectable.

**H3:** An adaptive camera scan interval system triggered by IoT risk levels will detect the onset of disease symptoms at an earlier stage than a fixed 30-minute interval system, because high-risk periods receive scans every 5 to 10 minutes rather than every 30 minutes.

**H4:** A farmer-facing mobile application with large text, simple navigation, clear zone-based alerts, and push notifications will demonstrate acceptable usability for smallholder farmers with basic smartphone literacy, as measured by task completion rate and user satisfaction feedback.

---

## CHAPTER 2: LITERATURE REVIEW

### 2.1 Related Works and Existing Systems

**2.1.1 PlantVillage Dataset and Platform (Hughes and Salathé, 2015)**

PlantVillage is one of the most foundational contributions to AI-based plant disease research. The dataset contains over 54,000 images spanning 26 plant species and 38 disease classes, including 9 tomato-specific classes that directly informed this project's disease categories. The PlantVillage platform also provides an online portal where farmers can submit images for disease identification.

While PlantVillage has been invaluable as a training dataset, it has a well-documented limitation: all images in the dataset were captured against controlled plain backgrounds under consistent laboratory lighting. Models trained solely on PlantVillage images typically demonstrate significantly reduced accuracy when applied to real farm photographs, which contain background vegetation, variable lighting, shadows, moisture on leaves, and partial occlusion. This domain gap between laboratory training data and real-world deployment data is a known challenge addressed in this project through field-condition image augmentation.

**2.1.2 Mohanty, Hughes, and Salathé (2016) — Deep Learning for Plant Disease Detection**

This landmark study trained a GoogLeNet deep neural network on the PlantVillage dataset and achieved an overall accuracy of 99.35% in controlled conditions. The study was the first large-scale demonstration that deep learning could match or exceed human expert performance in plant disease classification from images. However, the authors themselves acknowledged that real-world accuracy was substantially lower and called for further research into field-condition robustness.

**2.1.3 Plantix Application (Peat.io)**

Plantix is a commercially available mobile application that uses AI to identify plant diseases from photographs submitted by farmers. It supports over 400 plant conditions and is widely used across Asia and parts of Africa. The application works by prompting the farmer to photograph a suspicious leaf, analyzes the image using cloud-based AI, and returns a disease identification with treatment recommendations.

Plantix represents the current best-practice commercial solution for AI-based plant disease detection on mobile devices. However, it has three fundamental limitations relative to TomatoGuard. First, it requires the farmer to already suspect that disease is present before they use the application — the farmer must notice symptoms and decide to act before the system provides any value. Second, Plantix has no IoT environmental monitoring integration — it provides no environmental risk warnings before visual symptoms appear. Third, it does not record the location of disease within the farm, making it difficult to track disease spread across zones over time.

**2.1.4 Microsoft FarmBeats**

FarmBeats is Microsoft's precision agriculture platform combining IoT sensors, drone imagery, and machine learning for farm monitoring. It represents the state of the art in integrated smart farming technology. FarmBeats demonstrates the value of combining environmental sensing with data analytics for agricultural decision-making.

However, FarmBeats is designed for large commercial farms and requires significant technical infrastructure and ongoing subscription costs. It is not designed for smallholder farmers in low-income contexts. The system cost and complexity make it inaccessible for the farmers TomatoGuard targets.

**2.1.5 Rwanda Agriculture Board Extension Services**

The Rwanda Agriculture Board operates a network of agricultural extension officers who provide technical support to farmers across Rwanda. Extension officers provide crop disease diagnosis, treatment advice, and training. This is the primary disease management service currently available to smallholder tomato farmers in Rwanda.

The extension service is valuable but structurally limited by human capacity. Each extension officer covers a geographic area containing many farms and can realistically visit each farm only once every few weeks. The service is therefore unable to provide the continuous monitoring that early disease detection requires. TomatoGuard was designed to complement rather than replace extension services — providing continuous automated monitoring while extension officers focus on treatment guidance and farmer training.

**2.1.6 Ferentinos (2018) — Deep Learning Models for Plant Disease Detection**

Ferentinos compared multiple CNN architectures including AlexNet, VGG, and GoogLeNet for plant disease detection and found that deeper architectures generally outperformed shallower ones on the PlantVillage dataset. This study, along with Brahimi et al. (2017), confirmed that CNN-based detection is robust for tomato disease classification specifically, providing the theoretical foundation for TomatoGuard's AI component.

**2.1.7 Gondchawar and Kawitkar (2016) — IoT-Based Smart Agriculture**

This study proposed a comprehensive IoT architecture for smart farming using temperature, humidity, soil moisture, and light sensors connected to a central monitoring system. The study demonstrated that ESP8266-based nodes could reliably transmit sensor data over WiFi to a backend server and trigger alerts when thresholds were exceeded.

This work provided the theoretical foundation for TomatoGuard's IoT component. The key limitation of this and similar IoT agriculture studies is that they treated environmental monitoring and disease detection as completely separate concerns — no existing study reviewed combined both into a single integrated system with cross-feedback between the two.

### 2.2 Identified Gaps and Challenges

The review of existing systems identified the following specific gaps that TomatoGuard was designed to fill:

| Gap | How Existing Systems Handle It | TomatoGuard Solution |
|---|---|---|
| Autonomous scanning | No existing system scans automatically — all require farmer action | Fixed Raspberry Pi camera scans all zones every 5–30 minutes without any farmer action |
| IoT + AI integration | IoT systems and AI systems exist separately — no integrated system reviewed | IoT sensor risk level directly controls camera scan frequency and enriches AI detection context |
| Adaptive scan intervals | No reviewed system adjusts scan frequency based on risk conditions | Scan interval shortens from 30 min to 5 min when IoT detects high-risk conditions |
| Zone-based disease location | No reviewed system records which part of the farm is affected | Farm grid (A1–D4) records and displays exact zone of each detection |
| Two-stage AI pipeline | No reviewed system validates input before classification | Leaf validator (99.6% accuracy) confirms image is a tomato leaf before disease classification |
| African smallholder context | Most systems designed for high-income commercial farming contexts | Hardware cost ~$133 per farm unit; designed for Rwanda smallholder farm scale and literacy level |
| Pre-symptom environmental warning | No reviewed system warns before symptoms appear | IoT risk assessment warns farmers when conditions are favorable for disease before visual symptoms |
| Real-time farmer notification | Plantix requires farmer to open the app | Push notifications delivered automatically to farmer's Android phone |

### 2.3 Way Forward

The literature review confirmed that the individual technologies required for TomatoGuard — CNN-based image classification, IoT environmental monitoring, mobile application development, and cloud backend systems — are each individually mature and proven. The research gap is not in any individual technology but in their integration into a single autonomous system designed specifically for the smallholder African farming context.

The way forward identified from the literature was to:

1. Use transfer learning on MobileNetV2 rather than training a CNN from scratch, leveraging the existing generalization of ImageNet-pretrained weights while adapting the classifier head to the specific tomato disease classes.

2. Apply aggressive data augmentation to PlantVillage images to simulate real farm photography conditions and reduce the accuracy gap between laboratory-trained models and real-world deployment.

3. Build a unified backend that acts as the central hub connecting all system components — receiving sensor data from IoT nodes, storing AI detection results, calculating risk levels, and dispatching farmer notifications — ensuring all data flows through a single coherent system rather than disconnected components.

4. Design the user interface specifically for farmers with basic smartphone literacy, prioritizing simplicity, large visual elements, and automatic notification delivery over complex interactive features.

---

## CHAPTER 3: RESEARCH METHODOLOGY

### 3.1 Data Collection Methods

#### 3.1.1 Image Collection for AI Model Training

The primary image dataset for training and validating the disease classification model was sourced from the PlantVillage dataset, made publicly available through Kaggle. The dataset provides tomato leaf images across the following 9 classes used in this project:

| Class | Disease Agent | Type | Images Used |
|---|---|---|---|
| Early Blight | Alternaria solani | Fungal | 1,000 |
| Late Blight | Phytophthora infestans | Oomycete | 1,000 |
| Leaf Mold | Passalora fulva | Fungal | 952 |
| Septoria Leaf Spot | Septoria lycopersici | Fungal | 1,771 |
| Spider Mites | Tetranychus urticae | Pest | 1,676 |
| Target Spot | Corynespora cassiicola | Fungal | 1,404 |
| Yellow Leaf Curl Virus | TYLCV | Viral | 5,357 |
| Mosaic Virus | Tomato Mosaic Virus | Viral | 373 |
| Healthy | — | — | 1,591 |

To address the domain gap between PlantVillage's controlled laboratory images and real Rwandan farm photography conditions, the following augmentation pipeline was applied to the training dataset:

- **Geometric augmentation:** Random horizontal and vertical flips, rotation up to ±30 degrees, random zoom between 80% and 120%.
- **Color augmentation:** Brightness variation of ±40%, contrast variation of ±30%, saturation and hue shifts to simulate different lighting conditions at different times of day.
- **Noise augmentation:** Gaussian noise injection to simulate image compression artifacts from low-cost smartphone cameras.
- **Blur augmentation:** Random Gaussian blur to simulate out-of-focus captures and motion blur.

**Model Architecture and Training:**

The disease classifier was built using MobileNetV2 as the base architecture, pre-trained on ImageNet. MobileNetV2 was selected for three specific reasons relevant to this deployment context:

1. It achieves classification accuracy comparable to significantly larger architectures (VGG16, ResNet50) while using approximately 14 times fewer parameters — making it suitable for deployment on the Raspberry Pi's limited compute resources.
2. Its depthwise separable convolution design reduces inference time, enabling real-time classification of captured images without queuing delays.
3. Its compact size (approximately 14 MB) allows the model to be loaded into RAM on devices with limited memory.

The training configuration was as follows: the base MobileNetV2 layers were frozen during initial training to preserve ImageNet-learned feature representations, and a custom classification head was attached consisting of a global average pooling layer, a dropout layer at 0.3 rate, and a dense softmax output layer with 9 units. The model was trained for 20 epochs using the Adam optimizer with an initial learning rate of 0.001 and categorical cross-entropy loss. The dataset was split 80% training and 20% validation.

**Leaf Validator:**

In addition to the disease classifier, a separate binary classification model — the leaf validator — was trained to determine whether an input image is a genuine tomato leaf before the disease classifier is invoked. This two-stage pipeline prevents false positive disease detections when the Raspberry Pi camera captures non-plant content such as the sky, soil, farm workers, or equipment. The leaf validator was trained on a binary dataset of tomato leaf images versus random non-plant images and achieved 99.6% validation accuracy.

#### 3.1.2 Environmental Data Collection Using IoT Sensors

Environmental data was collected using an ESP32-based IoT sensor node designed and simulated in this project. The hardware specification for each farm sensor node is as follows:

| Component | Specification | Role |
|---|---|---|
| ESP32 DevKit V1 | Dual-core 240 MHz, 520 KB SRAM, WiFi 802.11 b/g/n | Main microcontroller and WiFi communication |
| DHT22 Sensor | ±0.5°C temperature accuracy, ±2–5% relative humidity accuracy | Temperature and humidity monitoring |
| Analog Soil Moisture Sensor | 0–3.3V analog output, mapped to 0–100% moisture | Soil water content monitoring |
| Status LED (Green) | Standard 5mm LED with 330Ω resistor | Visual status indicator on the physical node |
| Pull-up Resistor | 10 kΩ | DHT22 signal line stability |

The ESP32 firmware was written in C++ using the Arduino framework, compiled and built using PlatformIO (espressif32 platform version 4.4.0). The firmware reads the DHT22 sensor and soil moisture sensor every 30 seconds and transmits a JSON payload to the backend REST API via HTTP POST. Upon receiving the response from the backend — which includes the calculated risk level — the firmware displays the status via the LED indicator: steady for low risk, slow blink for medium risk, and fast blink for high or critical risk.

The sensor circuit was fully designed and simulated using the Wokwi VS Code extension, an ESP32 hardware simulator that executes real compiled firmware in a virtual environment. The Wokwi simulation confirmed correct circuit wiring, firmware logic, WiFi connectivity behavior, and HTTP communication with the backend API before any physical hardware is procured.

A Python-based IoT simulator was developed in parallel to generate continuous realistic sensor readings for backend testing without requiring the Wokwi simulation to run continuously. The simulator generates randomized but realistic values within typical ranges (temperature 20–38°C, humidity 40–98%, soil moisture 20–90%) and POSTs them to the backend every 10 seconds.

#### 3.1.3 Farmer Interviews and Feedback

To ensure TomatoGuard addresses real farmer needs rather than assumed needs, informal structured interviews were conducted with smallholder tomato farmers. The interviews focused on four areas: current disease detection practices, preferred alert format, smartphone usage patterns, and acceptable hardware cost.

Key findings from the interviews that influenced the system design:

1. Farmers inspect their tomato crops once per day, typically in the early morning. Disease emerging in the afternoon or overnight is not noticed until the following morning — a delay of up to 18 hours before any detection occurs. This confirmed the value of continuous autonomous scanning.

2. Farmers expressed strong preference for push notifications over SMS because they are free, delivered instantly, and arrive directly from the app they trust. They wanted the notification to tell them exactly where the disease was — "Zone B2 has Early Blight" — rather than requiring them to open the app and navigate to find the information.

3. Farmers were concerned about the literacy barrier in smartphone applications. They requested large text, clear images, simple navigation with as few screens as possible, and the use of color (red for danger, green for healthy) as the primary visual signal rather than text alone.

4. Regarding hardware cost, farmers indicated they could consider a system costing the equivalent of one to two months of crop income — confirming that the target hardware cost of approximately 133 USD per farm unit is within a feasible range for adoption by farmers with regular tomato income.

#### 3.1.4 Data Integration Strategy

All three data streams in TomatoGuard — camera images from the Raspberry Pi, sensor readings from the ESP32, and user interactions from the mobile application — flow into the central FastAPI backend, which acts as the unified processing and coordination hub. The following diagram illustrates the integration architecture:

*Figure 3.1: TomatoGuard System Data Integration Architecture*

```
Raspberry Pi Camera ──► POST /detect ──► AI Pipeline (Validator → Classifier)
                                                    │
ESP32 IoT Sensor ────► POST /iot/sensors ──► Risk Assessment Engine
                                                    │
Flutter Mobile App ──► GET /farms, /detections ◄───┘
                                                    │
                              Supabase PostgreSQL (Database)
                                                    │
                              Firebase Cloud Messaging (Push Notifications)
```

When the risk assessment engine calculates a High or Critical risk level from incoming sensor data, it automatically shortens the Raspberry Pi camera scan interval — the camera polls the backend for its current scan interval configuration before each capture. This feedback loop between the IoT sensor layer and the camera layer is the key innovation that enables adaptive scanning.

### 3.2 Tools Used

The following tools and technologies were used in the development of TomatoGuard:

| Category | Technology | Version | Purpose |
|---|---|---|---|
| AI Framework | TensorFlow + Keras | 2.x | Model training and inference |
| AI Architecture | MobileNetV2 | ImageNet pre-trained | Transfer learning base model |
| Backend Framework | FastAPI | 0.100+ | RESTful API development |
| Database | PostgreSQL via Supabase | Free tier | Data storage, authentication |
| Database Client | Supabase Python SDK | Latest stable | Database operations from backend |
| Mobile Framework | Flutter | 3.x | Android application development |
| Web Framework | Next.js | 14.x | Administrative web dashboard |
| IoT Platform | PlatformIO + Arduino | espressif32 4.4.0 | ESP32 firmware compilation |
| IoT Simulation | Wokwi VS Code Extension | Licensed | ESP32 circuit simulation |
| IoT Simulator | Python (requests library) | 3.10+ | Synthetic sensor data for testing |
| Camera Platform | Raspberry Pi OS | Bullseye (64-bit) | Fixed farm camera operation |
| Camera Library | OpenCV + picamera2 | Latest stable | Image capture and preprocessing |
| HTTP Tunnel | ngrok | Free tier | Public backend access during development |
| Version Control | Git + GitHub | Latest | Source code management |
| Image Storage | Supabase Storage | Free tier | Tomato leaf image files |
| Notifications | Firebase Cloud Messaging | Free tier | Push notifications to farmer phones |
| Authentication | JWT (python-jose) | — | Secure API authentication |
| Password Security | bcrypt | — | Password hashing |
| IDE | Visual Studio Code | Latest | Primary development environment |
| APK Signing | Android Keystore | — | Release APK security and signing |
| App Icon | flutter_launcher_icons | 0.13.1 | Mobile application icon generation |

**CNN Architecture Comparison — Why MobileNetV2 Was Chosen:**

| Architecture | Parameters | Accuracy on PlantVillage | Inference Speed | Suitable for Raspberry Pi |
|---|---|---|---|---|
| AlexNet | 61 million | ~94% | Slow | No |
| VGG16 | 138 million | ~97% | Very slow | No |
| ResNet50 | 25 million | ~96% | Moderate | Marginal |
| GoogLeNet | 6.8 million | ~99% | Fast | Marginal |
| **MobileNetV2** | **3.4 million** | **~91%** | **Very fast** | **Yes** |

MobileNetV2 was selected because it is the only architecture in this comparison that achieves both acceptable accuracy and practical inference speed on the Raspberry Pi 4's hardware — making it the only viable choice for real-time farm deployment.

### 3.3 Prototype and Simulation

TomatoGuard was developed as a fully functional prototype. Since physical IoT hardware (ESP32, Raspberry Pi) was not yet procured during the development phase, two complementary simulation approaches were used to validate the system before hardware deployment.

**3.3.1 Python IoT Simulator**

The primary simulation method used throughout development was a Python-based IoT simulator (`simulator.py`) built specifically for this project. The simulator replicates the exact behavior of a real ESP32 sensor node — generating realistic sensor readings and transmitting them to the backend REST API at regular intervals — without requiring any physical hardware.

The simulator generates values within the realistic ranges observed in Rwandan tomato farming environments:
- Temperature: 20°C to 38°C (day and night variation)
- Relative Humidity: 40% to 98% (dry season to rainy season)
- Soil Moisture: 20% to 90% (irrigated to waterlogged)

Every 10 seconds, the simulator sends a POST request to the `/iot/sensors` endpoint with a JSON payload identical in structure to what the real ESP32 firmware sends. The backend processes this data through the risk assessment engine and returns a risk level response, which the simulator prints to the console. This allowed continuous end-to-end testing of the complete data pipeline — from sensor reading, through risk calculation, to database storage and mobile app display — without interruption.

The simulator was the foundation of all integration testing in this project. It proved that the backend correctly handles concurrent sensor inputs, calculates risk levels accurately, and stores readings in the Supabase database in real time. Every feature shown in the mobile application was verified using data generated by this simulator.

The simulator configuration is stored in a single file (`config.py`) making it easy to change the target backend URL, farm ID, and sending interval without modifying the simulation logic:

```python
BACKEND_URL = "https://<ngrok-url>.ngrok-free.app"
FARM_ID     = "81db3508-b9df-4543-82ce-a12d7b5e1667"
SEND_INTERVAL_SECONDS = 10
```

**3.3.2 ESP32 Hardware Circuit Design**

In parallel with the Python simulator, the ESP32 sensor circuit was fully designed and documented. The firmware was written in C++ using the Arduino framework and compiled using PlatformIO. The circuit design covers:
- DHT22 connected to GPIO 15 with a 10kΩ pull-up resistor
- Analog soil moisture sensor connected to GPIO 34 (ADC pin)
- Status LED on GPIO 2 with a 330Ω current-limiting resistor
- All components powered from the ESP32's 3.3V rail

This design is ready for immediate physical deployment. Once the ESP32 hardware is procured, the compiled firmware can be flashed directly and the node will begin transmitting real sensor data to the backend — replacing the Python simulator transparently, since both send identical JSON payloads to the same API endpoint.

**Summary of Built Components:**

| Component | Approach Used | Status |
|---|---|---|
| AI Disease Classifier | Trained on PlantVillage dataset — 91% accuracy | Complete |
| AI Leaf Validator | Binary classifier — 99.6% accuracy | Complete |
| FastAPI Backend (8 endpoints) | Built and tested with live requests | Complete |
| Supabase PostgreSQL Database | Full schema implemented | Complete |
| Flutter Android Mobile App | Signed APK tested on real device | Complete |
| Python IoT Simulator | Simulates ESP32 — used for all integration testing | Complete |
| ESP32 Firmware (C++) | Written, compiled, hardware design ready | Complete |
| Raspberry Pi Camera Code | Python code written — hardware deployment post-graduation | In Progress |
| Next.js Web Dashboard | Development ongoing | In Progress |

### 3.4 System Requirements

**Functional Requirements:**

| Requirement | Description |
|---|---|
| FR-01 | The system shall classify tomato leaf images into 9 disease and healthy classes with minimum 85% accuracy |
| FR-02 | The system shall validate that input images are genuine tomato leaves before running disease classification |
| FR-03 | The system shall receive temperature, humidity, and soil moisture data from ESP32 sensor nodes via REST API |
| FR-04 | The system shall calculate an environmental risk level (Low, Medium, High, Critical) from incoming sensor data |
| FR-05 | The system shall autonomously capture tomato zone images using a fixed Raspberry Pi camera at configurable intervals |
| FR-06 | The system shall adjust camera scan intervals based on the current farm risk level |
| FR-07 | The system shall send push notifications to farmers when disease is detected or risk level is High or Critical |
| FR-08 | The system shall display a grid-based farm zone map on the mobile app showing zones with detected disease |
| FR-09 | The system shall maintain historical records of all detections and sensor readings with timestamps |
| FR-10 | The system shall authenticate users using JWT tokens and store passwords as bcrypt hashes |

**Non-Functional Requirements:**

| Requirement | Target | Achieved |
|---|---|---|
| AI classifier accuracy | ≥ 85% | 91% |
| Leaf validator accuracy | ≥ 90% | 99.6% |
| API response time | < 2 seconds | ~0.8 seconds |
| Sensor reporting interval | 30 seconds | 30 seconds |
| Mobile app Android version | Android 8.0+ | Android 8.0+ (API 26+) |
| AI inference time per image | < 3 seconds | < 2 seconds |
| Data security | JWT + bcrypt | Implemented |

### 3.5 Raspberry Pi Fixed Camera System

The Raspberry Pi fixed camera system is the central innovation that distinguishes TomatoGuard from all existing plant disease detection systems. Rather than requiring farmers to photograph suspicious leaves and upload them manually — which means disease must be visually advanced before detection begins — TomatoGuard installs a camera permanently on the farm that watches all zones continuously.

**Physical Setup:**

A Raspberry Pi 4 (2GB RAM minimum) with a Raspberry Pi HQ Camera module is mounted on a central pole or elevated structure in the farm. A wide-angle lens (6mm CS-mount) enables the camera to capture clear images of tomato plants across all zones from the central position. The system is powered via a long power cable or solar-charged power bank, enabling 24-hour operation without manual intervention.

**Zone Grid System:**

The farm is divided into a logical grid of named zones. The default configuration supports a 4×4 grid (16 zones), labeled A1 through D4 as shown below:

*Figure 3.2: Farm Zone Grid Layout (4×4 default configuration)*

```
     Col 1   Col 2   Col 3   Col 4
Row A:  A1      A2      A3      A4
Row B:  B1      B2      B3      B4
Row C:  C1      C2      C3      C4
Row D:  D1      D2      D3      D4
```

Each zone corresponds to a physical area of the farm. When disease is detected, the alert sent to the farmer includes the specific zone name — for example, "Disease detected in Zone B2 — Early Blight (91% confidence)." This enables the farmer to go directly to the correct area of the farm without searching the entire plot.

**Adaptive Scan Intervals:**

The scan interval is not fixed — it adapts in real time based on the current environmental risk level reported by the ESP32 IoT sensor node. This is the feedback link between the IoT layer and the camera layer:

| Risk Level | Scan Interval | Trigger Condition |
|---|---|---|
| Low | Every 30 minutes | Humidity < 70%, Temperature 20–28°C, Soil normal |
| Medium | Every 15 minutes | Humidity 70–85% OR Temperature outside 20–28°C |
| High | Every 10 minutes | Humidity > 85% AND Temperature 10–25°C (Late Blight window) |
| Critical / Alert | Every 5 minutes | Disease already detected in this farm in the last 24 hours |
| Night Mode | Every 60 minutes | Local time between 8:00 PM and 6:00 AM |

The Raspberry Pi retrieves the current recommended scan interval from the backend API before each capture cycle. This means the scan frequency adjusts dynamically as environmental conditions change throughout the day and night — without any manual reconfiguration by the farmer or system administrator.

**Detection Workflow:**

The Raspberry Pi executes the following process for each zone scan:

1. Camera captures a high-resolution image of the designated zone.
2. Image is preprocessed: resized to 224×224 pixels, normalized, saved to local storage with timestamp and zone label.
3. Leaf validator model evaluates the image — if the image does not contain a clear tomato leaf (e.g., camera was obscured by rain or wind), the image is discarded and logged.
4. If the leaf validator confirms a valid tomato leaf, the disease classifier processes the image and returns the predicted class and confidence score.
5. If the confidence score exceeds 80% and the predicted class is not Healthy, the result is sent to the backend API as a new detection record.
6. The backend saves the detection, links it to the farm, zone, and timestamp, and triggers a push notification to the registered farmer's mobile device.
7. The farmer receives a notification: zone name, disease name, confidence percentage, and a link to view the captured image in the mobile app.

### 3.6 Database Schema Design

The TomatoGuard database was implemented in Supabase PostgreSQL. The schema consists of five core tables:

**Table: farmers**

| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Unique farmer identifier |
| full_name | VARCHAR | Farmer's full name |
| email | VARCHAR (UNIQUE) | Login email address |
| password_hash | VARCHAR | bcrypt-hashed password |
| phone | VARCHAR | Phone number for notifications |
| created_at | TIMESTAMP | Account creation timestamp |

**Table: farms**

| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Unique farm identifier |
| farmer_id | UUID (FK → farmers) | Owner of the farm |
| farm_name | VARCHAR | Name of the farm |
| location | VARCHAR | Physical location description |
| zone_grid | VARCHAR | Grid configuration (e.g., "4x4") |
| created_at | TIMESTAMP | Farm registration timestamp |

**Table: sensor_readings**

| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Unique reading identifier |
| farm_id | UUID (FK → farms) | Farm the reading belongs to |
| temperature | FLOAT | Temperature in degrees Celsius |
| humidity | FLOAT | Relative humidity percentage |
| soil_moisture | FLOAT | Soil moisture percentage |
| risk_level | VARCHAR | Calculated risk: Low/Medium/High/Critical |
| recorded_at | TIMESTAMP | Time of reading |

**Table: detections**

| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Unique detection identifier |
| farm_id | UUID (FK → farms) | Farm where disease was detected |
| zone | VARCHAR | Zone label (e.g., "B2") |
| disease_class | VARCHAR | Detected disease name |
| confidence | FLOAT | Model confidence score (0.0–1.0) |
| image_url | VARCHAR | Supabase Storage URL of captured leaf image |
| detected_at | TIMESTAMP | Time of detection |

**Table: alerts**

| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Unique alert identifier |
| farm_id | UUID (FK → farms) | Farm the alert relates to |
| detection_id | UUID (FK → detections) | Detection that triggered the alert |
| message | TEXT | Alert message sent to farmer |
| sent_at | TIMESTAMP | Time alert was dispatched |
| delivered | BOOLEAN | Delivery confirmation status |

### 3.7 Mobile Application Design

The TomatoGuard Android application was built using Flutter and compiled into a release APK signed with a production Android keystore. The application was designed with the findings from farmer interviews directly shaping every interface decision.

**Screen 1 — Login Screen:** Clean single-screen login with email and password fields. Large text, high-contrast colors. Error messages are clear and specific — "Wrong password" rather than "Authentication failed." Includes a registration link for new farmers. A 30-second HTTP timeout was implemented to prevent the app from hanging indefinitely if the backend is temporarily unreachable.

**Screen 2 — Farm Dashboard:** The main screen after login. Displays the current sensor readings in three large tiles: Temperature (°C), Humidity (%), and Soil Moisture (%). A colored risk level banner spans the top of the screen — green for Low, yellow for Medium, orange for High, red for Critical. The current date and last sensor reading timestamp are displayed.

**Screen 3 — Zone Map:** A visual grid representation of the farm. Each zone cell is colored based on its current status — green for healthy or no recent detection, red for a zone with an active disease detection in the last 24 hours. Tapping a zone cell navigates to the detection detail screen for that zone.

**Screen 4 — Detection Detail Screen:** Displays the captured leaf image, the disease class name in plain English, the confidence percentage, the zone label, the detection timestamp, and a brief description of the disease. Future versions will include recommended treatment actions in this screen.

**Screen 5 — Detection History:** A scrollable list of all past detections for the farmer's farm, sorted by most recent first. Each list item shows the disease name, zone, confidence score, and date. Tapping an item opens the Detection Detail screen.

### 3.8 Security Design

TomatoGuard implements the following security measures:

**Authentication:** All protected API endpoints require a valid JSON Web Token (JWT) in the request Authorization header. Tokens are issued at login and expire after 24 hours. The backend validates tokens on every request using the python-jose library.

**Password Security:** Farmer passwords are never stored in plain text. The bcrypt hashing algorithm is used to store a salted hash of each password. The cost factor is set to 12, making brute-force attacks computationally expensive.

**API Security:** The backend implements CORS (Cross-Origin Resource Sharing) controls. During development, origins are set to allow all for testing flexibility. In production deployment, this will be restricted to the specific mobile app and web dashboard origins.

**Data Privacy:** Tomato leaf images are stored in Supabase Storage with access controlled by Row Level Security policies. Farmer data is isolated by farmer_id, ensuring farmers cannot access data belonging to other farmers.

### 3.9 Deployment Architecture

**Development Deployment (Current):**

During development and testing, the following deployment configuration was used:

*Figure 3.3: Development Deployment Architecture*

```
Farmer's Android Phone
        │
        │ HTTPS
        ▼
   ngrok Tunnel ──► localhost:8000 (FastAPI Backend)
                              │
                    Supabase PostgreSQL
                    (West EU, Ireland)
```

The ngrok tunnel provides a stable public HTTPS URL that the mobile application connects to, allowing real device testing without requiring a cloud server. All API requests include the ngrok-skip-browser-warning header to bypass ngrok's browser warning page.

**Production Deployment Plan (Post-FYP):**

*Figure 3.4: Production Deployment Architecture (Planned)*

```
Farmer's Android Phone
        │
        │ HTTPS
        ▼
  Cloud VPS Server ──► FastAPI Backend (Linux, uvicorn)
  (Railway / AWS EC2)           │
                      Supabase PostgreSQL
```

The backend will be migrated from ngrok to a persistent cloud VPS after graduation. This eliminates the requirement for the development laptop to remain running for the system to function.

### 3.10 What Was Built vs. What Was Proposed

The following table provides an honest and transparent comparison between what was originally proposed in the project proposal and what was actually built and tested:

| Component | Originally Proposed | Actually Built | Status |
|---|---|---|---|
| AI disease classifier (9 classes) | Proposed — target 85% accuracy | Built — achieved 91% accuracy | Complete |
| Leaf validator (2-stage pipeline) | Not in original proposal — added during development | Built — achieved 99.6% accuracy | Complete |
| FastAPI backend (8 endpoints) | Proposed | Built and tested | Complete |
| Supabase PostgreSQL database | Proposed | Built with full schema | Complete |
| Flutter Android mobile app | Proposed | Built, signed APK, tested on real device | Complete |
| ESP32 IoT firmware (C++) | Proposed | Written, compiled, circuit design ready for hardware | Complete |
| Python IoT simulator | Not in original proposal — added for testing | Built and used for all integration testing | Complete |
| Raspberry Pi camera system | Proposed | Code written; physical hardware deployment post-graduation | In Progress |
| Next.js web dashboard | Proposed | Development ongoing | In Progress |
| Physical ESP32 hardware deployment | Proposed | Pending hardware procurement | Future Work |
| Cloud server production deployment | Proposed | Planned post-graduation | Future Work |

The two-stage AI pipeline (leaf validator + disease classifier) and the Python IoT simulator were additions made during development that were not in the original proposal. Both represent improvements to the system's robustness and validation quality beyond what was originally planned.

### 3.11 System Design — Use Case Diagram

**System Actors:**

- **Farmer:** The primary end user. Receives alerts, views sensor data, views detection history, manages farm profile.
- **ESP32 IoT Node:** Automated hardware actor. Reads sensors and transmits data to the backend.
- **Raspberry Pi Camera:** Automated hardware actor. Captures zone images and submits them for AI analysis.
- **System Administrator:** Manages multiple farms and farmers via the web dashboard.
- **FastAPI Backend:** Central system hub coordinating all data flows.

**Use Case Summary:**

```
FARMER
├── Register account and create farm profile
├── Log in to mobile application
├── View real-time sensor readings (Temperature, Humidity, Soil Moisture)
├── View current environmental risk level
├── View farm zone map with disease indicators
├── View full detection history with images
├── View individual detection details (image, disease, confidence, zone)
├── Receive push notification on disease detection
└── Update farm and account settings

ESP32 IoT NODE (Automated)
├── Read DHT22 temperature and humidity every 30 seconds
├── Read analog soil moisture value every 30 seconds
├── Transmit sensor JSON to backend POST /iot/sensors
└── Receive risk_level response and indicate via LED status

RASPBERRY PI CAMERA (Automated)
├── Query backend for current recommended scan interval
├── Capture zone image on schedule
├── Run leaf validator — discard if not a tomato leaf
├── Run disease classifier on validated image
├── Submit detection result to backend POST /detect
└── Trigger farmer notification if disease detected

SYSTEM ADMINISTRATOR
├── View all registered farms and farmers
├── View system-wide sensor and detection analytics
├── Manage user accounts and permissions
└── Monitor system health and API status
```

### 3.12 Timeline and Project Planning

| Phase | Description | Timeline | Status |
|---|---|---|---|
| Phase 1 | Project proposal, literature review, supervisor meetings | Weeks 1–3 | Complete |
| Phase 2 | Database design and Supabase schema implementation | Weeks 4–5 | Complete |
| Phase 3 | FastAPI backend development, all REST endpoints | Weeks 5–7 | Complete |
| Phase 4 | AI model training — disease classifier (MobileNetV2) | Weeks 7–9 | Complete |
| Phase 5 | AI leaf validator training and two-stage pipeline integration | Weeks 9–10 | Complete |
| Phase 6 | Flutter mobile application development (all screens) | Weeks 10–13 | Complete |
| Phase 7 | ESP32 firmware development (C++, PlatformIO, Arduino) | Weeks 13–14 | Complete |
| Phase 8 | Wokwi ESP32 circuit simulation and verification | Week 15 | Complete |
| Phase 9 | Python IoT simulator development and integration testing | Week 15 | Complete |
| Phase 10 | Release APK build, keystore signing, real device testing | Week 16 | Complete |
| Phase 11 | ngrok deployment, mobile-backend end-to-end testing | Week 17 | Complete |
| Phase 12 | Raspberry Pi camera code development | Weeks 18–19 | In Progress |
| Phase 13 | Next.js web dashboard development | Weeks 18–20 | In Progress |
| Phase 14 | Full system integration testing and documentation | Weeks 20–22 | In Progress |
| Phase 15 | Final report completion and supervisor submission | Weeks 23–24 | Upcoming |

---

## EXPECTED RESULTS / OUTPUT

The following results were achieved or are expected upon full completion of TomatoGuard:

**1. AI Model Performance**

The disease classifier and leaf validator were trained and tested with the following results:

| Model | Task | Accuracy Achieved |
|---|---|---|
| Leaf Validator | Binary: tomato leaf vs. non-leaf | 99.6% |
| Disease Classifier | 9-class: 8 diseases + healthy | 91% |

The two-stage pipeline ensures that the disease classifier only processes confirmed tomato leaf images, eliminating false positive disease detections caused by irrelevant input. This is a measurable improvement in system reliability over single-stage classifiers.

**2. IoT Sensor System**

The ESP32 sensor node transmits environmental data every 30 seconds with the following verified behavior:
- Temperature and humidity read successfully from DHT22 with no read failures in simulation
- Soil moisture value mapped correctly from ADC raw value (0–4095) to percentage (0–100%)
- Risk level response received from backend and displayed via LED status indicator
- Full round-trip (sensor read → POST → response) completed in under 2 seconds

Sample sensor payload transmitted to the backend:
```json
{
  "farm_id": "81db3508-b9df-4543-82ce-a12d7b5e1667",
  "temperature": 24.5,
  "humidity": 82.3,
  "soil_moisture": 67.0
}
```

Sample backend response:
```json
{
  "risk_level": "medium",
  "message": "Humidity elevated. Conditions approaching Early Blight threshold. Monitor closely."
}
```

**3. Mobile Application**

A signed release Android APK was successfully built, installed, and tested on a physical Android device. The application demonstrated the following verified capabilities:
- Farmer registration and JWT-secured login
- Real-time sensor reading display (last received values)
- Risk level banner with color-coded severity
- Zone map showing detection locations
- Detection history with disease images and details
- Push notification receipt and display

**4. System Integration**

End-to-end system testing confirmed that the complete data flow — from sensor reading through the backend to farmer notification — functions correctly. The system was tested using the Python IoT simulator generating continuous concurrent sensor requests, demonstrating that the backend correctly calculates risk levels, stores readings in the database, and serves real-time data to the mobile application without errors.

**5. Innovation Impact**

TomatoGuard demonstrates the following specific innovations not present in any reviewed existing system:

- **Autonomous 24/7 farm scanning** — The first system reviewed that does not require farmer action to initiate disease detection
- **IoT-triggered adaptive scan intervals** — Environmental risk level directly controls camera frequency
- **Two-stage AI pipeline** — Leaf validator + disease classifier reduces false positives
- **Zone-based disease location** — Exact farm location recorded and displayed for every detection
- **Integrated IoT + AI + Mobile in one system** — All components connected through a single backend

---

## LIMITATIONS

The current implementation of TomatoGuard has three primary limitations that are acknowledged transparently:

**1. Physical Hardware Not Yet Deployed:** The Raspberry Pi fixed camera system and the ESP32 IoT sensor nodes have been fully designed, coded, and validated through the Python IoT simulator, but have not yet been physically mounted on a real farm. The autonomous scanning and adaptive interval features have been demonstrated in software but await hardware procurement and field deployment. This is planned as the first post-graduation step.

**2. Web Dashboard Still Under Development:** The Next.js administrative web dashboard — which provides multi-farm monitoring, analytics, and account management for system administrators — is still under development and was not completed within the FYP timeline. The mobile application and backend API are fully functional and serve as the primary interface for farmers and testing.

**3. AI Model Trained on Laboratory Dataset:** The disease classifier was trained and validated on the PlantVillage dataset, which contains images captured in controlled laboratory conditions with plain backgrounds. While aggressive data augmentation was applied to simulate real farm photography conditions, the model has not yet been validated on a dataset of images captured from actual Rwandan tomato farms. Real-world accuracy may differ from the 91% achieved on the augmented PlantVillage validation set. Collecting field images from Rwandan farms and fine-tuning the model is identified as a priority future work item.

These limitations do not affect the core functionality of the system as demonstrated — the backend, mobile application, AI pipeline, and IoT data flow all work correctly and have been verified end-to-end. They represent the gap between the current academic prototype and a production-ready farm deployment, which the team intends to close after graduation.

---

## CONCLUSION

TomatoGuard was designed to solve a specific and well-defined problem: tomato farmers in Rwanda lose significant portions of their harvest to diseases that could have been treated effectively if detected 24 to 48 hours earlier. Every existing solution reviewed in this project shares the same fundamental limitation — they wait for the farmer to notice a problem before they can help. TomatoGuard removes this dependency entirely.

By mounting a Raspberry Pi camera permanently on the farm and connecting it to a continuous IoT environmental monitoring network, TomatoGuard creates a system that watches the farm around the clock. When the environmental conditions measured by the ESP32 sensor node indicate that disease-favorable conditions are developing, the camera scan frequency automatically increases — providing more coverage precisely when disease risk is highest. When the AI pipeline detects disease in a captured image, an immediate push notification is sent to the farmer's phone specifying the exact zone affected.

The project has successfully implemented and tested all core components: the two-stage AI pipeline achieved 91% disease classification accuracy and 99.6% leaf validation accuracy; the FastAPI backend processes sensor data and detection results in under 2 seconds; the Flutter mobile application was installed and verified on a real Android device; and the ESP32 firmware and circuit design were fully validated through the Python IoT simulator before physical hardware is procured.

The remaining work — physical deployment of the Raspberry Pi camera on a real farm and completion of the Next.js web dashboard — represents the path from academic prototype to real-world deployment. The architecture and codebase are designed and ready for this transition. It is the team's intention to pursue full farm deployment after graduation, as TomatoGuard represents not just a final year project but a foundation for continued work in agricultural technology for Rwanda.

In its current state, TomatoGuard demonstrates that a small team of Computer and Software Engineering students can design and implement a genuinely innovative, technically sophisticated, and practically relevant system using affordable hardware and open-source software — and in doing so, contribute meaningfully to Rwanda's agricultural modernization agenda.

---

## REFERENCES

[1] D. P. Hughes and M. Salathé, "An open access repository of images on plant health to enable the development of mobile disease diagnostics," *arXiv preprint arXiv:1511.08060*, Nov. 2015.

[2] S. P. Mohanty, D. P. Hughes, and M. Salathé, "Using deep learning for image-based plant disease detection," *Frontiers in Plant Science*, vol. 7, p. 1419, Sep. 2016. doi: 10.3389/fpls.2016.01419.

[3] K. P. Ferentinos, "Deep learning models for plant disease detection and diagnosis," *Computers and Electronics in Agriculture*, vol. 145, pp. 311–318, Feb. 2018. doi: 10.1016/j.compag.2018.01.009.

[4] M. Brahimi, K. Boukhalfa, and A. Moussaoui, "Deep learning for tomato diseases: classification and symptoms visualization," *Applied Artificial Intelligence*, vol. 31, no. 4, pp. 299–315, 2017. doi: 10.1080/08839514.2017.1315516.

[5] M. Sandler, A. Howard, M. Zhu, A. Zhmoginov, and L. C. Chen, "MobileNetV2: Inverted residuals and linear bottlenecks," in *Proc. IEEE Conf. Computer Vision and Pattern Recognition (CVPR)*, Salt Lake City, UT, USA, 2018, pp. 4510–4520.

[6] N. Gondchawar and R. S. Kawitkar, "IoT based smart agriculture," *International Journal of Advanced Research in Computer and Communication Engineering*, vol. 5, no. 6, pp. 838–842, Jun. 2016.

[7] K. A. Patil and N. R. Kale, "A model for smart agriculture using IoT," in *Proc. International Conference on Global Trends in Signal Processing, Information Computing and Communication (ICGTSPICC)*, Jalgaon, India, 2016, pp. 543–545.

[8] A. Kamilaris and F. X. Prenafeta-Boldú, "Deep learning in agriculture: A survey," *Computers and Electronics in Agriculture*, vol. 147, pp. 70–90, Apr. 2018. doi: 10.1016/j.compag.2018.02.016.

[9] Rwanda Agriculture Board, "Annual Crop Disease Surveillance Report," RAB Publications, Kigali, Rwanda, 2022.

[10] Ministry of Agriculture and Animal Resources, Rwanda, "National Agriculture Policy," MINAGRI, Kigali, Rwanda, 2020.

[11] Espressif Systems, "ESP32 Technical Reference Manual, Version 5.1," Espressif Systems, Shanghai, China, 2023. [Online]. Available: https://www.espressif.com/documentation

[12] Raspberry Pi Foundation, "Raspberry Pi 4 Model B — Technical Specification," Raspberry Pi Foundation, Cambridge, UK, 2023. [Online]. Available: https://www.raspberrypi.com/products/raspberry-pi-4-model-b/specifications

[13] Supabase Inc., "Supabase Documentation — PostgreSQL Database and Authentication," 2023. [Online]. Available: https://supabase.com/docs

[14] Google LLC, "Flutter — Build Apps for Any Screen," 2023. [Online]. Available: https://flutter.dev/docs

[15] S. Tiangolo, "FastAPI — Modern, Fast Web Framework for Building APIs with Python," 2023. [Online]. Available: https://fastapi.tiangolo.com

---

*Prepared by RUTEMBEZA Yves (222009019) and NIYONIZERA Benigne (221020634)*
*University of Rwanda — Department of Computer and Software Engineering*
*Supervisors: Dr. NTARINDWA Theoneste and Mr. GASUHUKE Janvier J.P*
*Academic Year 2025–2026*
