# Brain MRI Classification System - Backend

Flask API for brain tumor detection using ResNet50 + Grad-CAM explainability.

## 📁 Project Structure

```
backend/
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (local config)
├── models/
│   ├── resnet50_model.py   # ResNet50 model loader
│   ├── gradcam.py          # Grad-CAM implementation
│   └── resnet50_best.pth   # Trained model weights (99.31% accuracy)
├── routes/
│   ├── auth.py             # Authentication endpoints
│   └── predict.py          # Prediction endpoints
├── database/
│   ├── db.py               # Database utilities
│   └── schema.sql          # MySQL schema
├── utils/
│   ├── preprocessing.py    # Image preprocessing
│   └── storage.py          # File storage utilities
├── uploads/                # Uploaded MRI images
└── gradcam_outputs/        # Generated Grad-CAM visualizations
```

## 🚀 Quick Start

### 1. Setup Database (MySQL)

```bash
# Start XAMPP MySQL server, then run:
mysql -u root -p < database/schema.sql
```

This creates `brain_mri_db` with sample users:
- Admin: `admin@test.com` / `admin123`
- Doctor: `doctor@test.com` / `admin123`
- Patient: `patient@test.com` / `admin123`

### 2. Configure Environment

Edit `.env` file (already created from `.env.example`):
```env
DB_HOST=localhost
DB_PASSWORD=your_mysql_password_here
SECRET_KEY=your-secret-key-change-this
```

### 3. Activate Virtual Environment & Run Server

```bash
# Activate venv
venv\Scripts\activate

# Start Flask server
python app.py
```

Server runs at: **http://localhost:5000**

## 🧪 Testing

### Option 1: Test Script (Automated)

```bash
# Make sure server is running in another terminal first!
python test_api.py
```

### Option 2: Manual Testing (cURL/Postman)

**1. Health Check:**
```bash
curl http://localhost:5000/health
```

**2. Login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"doctor@test.com\",\"password\":\"admin123\"}" \
  -c cookies.txt
```

**3. Upload MRI for Prediction:**
```bash
curl -X POST http://localhost:5000/api/predict \
  -F "image=@path/to/mri_image.jpg" \
  -b cookies.txt
```

**4. Get Prediction History:**
```bash
curl http://localhost:5000/api/predictions/history -b cookies.txt
```

**5. Logout:**
```bash
curl -X POST http://localhost:5000/api/auth/logout -b cookies.txt
```

## 📡 API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Health check | No |
| POST | `/api/auth/login` | User login | No |
| POST | `/api/auth/logout` | User logout | Yes |
| GET | `/api/auth/me` | Get current user | Yes |
| POST | `/api/auth/register` | Create user (admin only) | Yes (Admin) |
| POST | `/api/predict` | Upload MRI & get prediction | Yes |
| GET | `/api/predictions/<id>` | Get specific prediction | Yes |
| GET | `/api/predictions/history` | Get prediction history | Yes |

## 🔧 Configuration

### Database (.env)
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=brain_mri_db
```

### Model (.env)
```env
MODEL_PATH=models/resnet50_best.pth
IMG_SIZE=224
```

### Storage (.env)
```env
UPLOAD_FOLDER=uploads
GRADCAM_FOLDER=gradcam_outputs
```

## 🧠 Model Information

- **Architecture:** ResNet50 (transfer learning from ImageNet)
- **Task:** Binary classification (tumor vs no_tumor)
- **Accuracy:** 99.31% on test set
- **Input:** 224×224 RGB MRI images
- **Normalization:** ImageNet stats ([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
- **Explainability:** Grad-CAM heatmaps from layer4[-1]

## 📦 Dependencies

Key packages (see `requirements.txt` for full list):
- Flask 3.0.0 (web framework)
- PyTorch 2.1.0 (deep learning)
- OpenCV 4.8.1 (image processing)
- PyMySQL 1.1.0 (database)
- bcrypt 4.1.1 (password hashing)

## 🐛 Troubleshooting

**Database connection error:**
- Check XAMPP MySQL is running
- Verify `.env` DB_PASSWORD matches your MySQL root password
- Test connection: `mysql -u root -p`

**Model not found:**
- Verify `models/resnet50_best.pth` exists (should be ~90MB)
- Check `MODEL_PATH` in `.env`

**Import errors:**
- Activate venv: `venv\Scripts\activate`
- Reinstall: `pip install -r requirements.txt`

**CORS errors (when testing with frontend):**
- Check `CORS_ORIGINS` in `config.py` includes your frontend URL

## ☁️ Azure Deployment (Future)

When deploying to Azure:
1. Change storage in `utils/storage.py` to Azure Blob
2. Update database to Azure Database for MySQL
3. Deploy Flask app to Azure App Service
4. Update CORS origins for production domain

## 📝 License

Educational/Research use only. Not for clinical deployment without proper validation.
