from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import UserRegistrationModel
from django.conf import settings
import os
# import pickle
# Create your views here.
import re


def UserRegisterActions(request):
    if request.method == 'POST':

        name = request.POST.get('name')
        loginid = request.POST.get('loginid')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        locality = request.POST.get('locality')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')

        # -----------------------------
        # VALIDATIONS
        # -----------------------------

        # 1. Mobile validation (Indian)
        if not re.match(r'^[6-9][0-9]{9}$', mobile):
            messages.error(request, "Invalid mobile number. Must be 10 digits and start with 6-9.")
            return render(request, 'UserRegistrations.html')

        # 2. Password validation
        if not re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$', password):
            messages.error(request, "Password must have 1 capital letter, 1 number, 1 special symbol, and be at least 8 characters long.")
            return render(request, 'UserRegistrations.html')

        # 3. Check duplicate login ID
        if UserRegistrationModel.objects.filter(loginid=loginid).exists():
            messages.error(request, "Login ID already taken. Try another.")
            return render(request, 'UserRegistrations.html')

        # 4. Check duplicate mobile
        if UserRegistrationModel.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile number already registered.")
            return render(request, 'UserRegistrations.html')

        # 5. Check duplicate email
        if UserRegistrationModel.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'UserRegistrations.html')

        # -----------------------------
        # SAVE DATA
        # -----------------------------
        UserRegistrationModel.objects.create(
            name=name,
            loginid=loginid,
            password=password,
            mobile=mobile,
            email=email,
            locality=locality,
            address=address,
            city=city,
            state=state,
            status='waiting'
        )

        messages.success(request, "Registration successful!")
        return render(request, 'UserRegistrations.html')

    return render(request, 'UserRegistrations.html')

def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                print("User id At", check.id, status)
                return render(request, 'users/UserHomePage.html', {})
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'UserLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            messages.success(request, 'Invalid Login id and password')
    return render(request, 'UserLogin.html', {})

def UserHome(request):
    return render(request, 'users/UserHomePage.html', {})

def DatasetView(request):
    path = os.path.join(BASE_DIR, 'ml_model', 'test_data.csv')
    df = pd.read_csv(path)
    df = df.drop(columns=['Subject ID', 'MRI ID', 'Hand'], errors='ignore')   # ← add this line
    df_html = df.to_html(classes='table table-striped', index=False)
    return render(request, 'users/viewdataset.html', {'data': df_html})

# import os
# import pandas as pd
# import joblib
# from django.shortcuts import render
# from django.core.files.storage import FileSystemStorage
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.preprocessing import LabelEncoder, OneHotEncoder
# from sklearn.model_selection import train_test_split
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# # Training view
# import os
# import pandas as pd
# import joblib
# from django.shortcuts import render
# from django.core.files.storage import FileSystemStorage
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.preprocessing import LabelEncoder, OneHotEncoder
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score, confusion_matrix
# import seaborn as sns
# import matplotlib.pyplot as plt

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# def Training(request):
#     message = ''
#     accuracy = None
#     confusion_img_path = None

#     if request.method == 'POST' and request.FILES.get('file'):
#         file = request.FILES['file']
#         fs = FileSystemStorage()
#         file_path = fs.save(file.name, file)
#         data = pd.read_csv(fs.path(file_path))

#         # Drop irrelevant columns
#         data = data.drop(['Subject ID', 'MRI ID', 'Hand'], axis=1)

#         # Split features and label
#         X = data.drop('class', axis=1)
#         y = data['class']

#         # One-hot encode 'M/F'
#         ohe = OneHotEncoder()
#         gender_encoded = ohe.fit_transform(X[['M/F']]).toarray()
#         gender_df = pd.DataFrame(gender_encoded, columns=ohe.get_feature_names_out(['M/F']))
#         X = X.drop('M/F', axis=1).reset_index(drop=True)
#         X = pd.concat([X, gender_df], axis=1)

#         # Label encode target
#         le = LabelEncoder()
#         y = le.fit_transform(y)

#         # Train model
#         X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#         model = RandomForestClassifier()
#         model.fit(X_train, y_train)

#         # Predict and calculate accuracy
#         y_pred = model.predict(X_test)
#         accuracy = accuracy_score(y_test, y_pred)

#         # Generate and save confusion matrix plot
#         cm = confusion_matrix(y_test, y_pred)
#         plt.figure(figsize=(6, 4))
#         sns.heatmap(cm, annot=True, fmt='d', cmap='Purples', xticklabels=le.classes_, yticklabels=le.classes_)
#         plt.title("Confusion Matrix")
#         plt.xlabel("Predicted")
#         plt.ylabel("Actual")
#         plot_path = os.path.join(BASE_DIR, 'static', 'images', 'confusion_matrix.png')
#         os.makedirs(os.path.dirname(plot_path), exist_ok=True)
#         plt.savefig(plot_path)
#         plt.close()

#         confusion_img_path = 'confusion_matrix.png'

#         # Save model and encoders
#         joblib.dump(model, os.path.join(BASE_DIR, 'model.pkl'))
#         joblib.dump(le, os.path.join(BASE_DIR, 'label_encoder.pkl'))
#         joblib.dump(ohe, os.path.join(BASE_DIR, 'ohe_encoder.pkl'))

#         message = "Model trained and saved successfully!"

#     return render(request, 'users/train.html', {
#         'message': message,
#         'accuracy': accuracy,
#         'confusion_img_path': confusion_img_path
#     })


# # Prediction view
# def Prediction(request):
#     prediction = None
#     if request.method == 'POST' and request.FILES.get('file'):
#         file = request.FILES['file']
#         fs = FileSystemStorage()
#         file_path = fs.save(file.name, file)
#         df = pd.read_csv(fs.path(file_path))

#         # Drop irrelevant columns
#         df = df.drop(['Subject ID', 'MRI ID', 'Hand'], axis=1)

#         # Load encoders and model
#         model = joblib.load(os.path.join(BASE_DIR, 'ml_model/model.pkl'))
#         le = joblib.load(os.path.join(BASE_DIR, 'ml_model/label_encoder.pkl'))
#         ohe = joblib.load(os.path.join(BASE_DIR, 'ml_model/ohe_encoder.pkl'))

#         # One-hot encode gender
#         gender_encoded = ohe.transform(df[['M/F']]).toarray()
#         gender_df = pd.DataFrame(gender_encoded, columns=ohe.get_feature_names_out(['M/F']))
#         df = df.drop('M/F', axis=1).reset_index(drop=True)
#         df = pd.concat([df, gender_df], axis=1)

#         # Predict
#         preds = model.predict(df)
#         prediction = le.inverse_transform(preds)

#         df['Predicted Class'] = prediction
#         prediction = df.to_html(classes="table table-bordered")

#     return render(request, 'users/predict.html', {'prediction': prediction})


import joblib
import pandas as pd
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from django.core.files.storage import FileSystemStorage
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split




from django.core.files.storage import FileSystemStorage

import joblib

from sklearn.linear_model import LogisticRegression

BASE_DIR = settings.BASE_DIR  # Ensure this is defined in settings.py 

import matplotlib
matplotlib.use('Agg')

from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

def Training(request):
    try:
        context = {}

        print("STEP 1: Loading dataset...")
        df = pd.read_csv(os.path.join(BASE_DIR, 'ml_model', 'test_data.csv'))

        print("STEP 2: Preprocessing...")

        df['Group'] = df['Group'].replace({
            'Nondemented': 0,
            'Demented': 1,
            'Converted': 2
        })

        df = df[df['Group'].isin([0, 1])]
        df = df.drop(columns=['Subject ID', 'MRI ID', 'Hand'], errors='ignore')

        for col in df.select_dtypes(include=['float64', 'int64']).columns:
            df[col] = df[col].fillna(df[col].median())

        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].fillna(df[col].mode()[0])

        df = pd.get_dummies(df, drop_first=True)

        X = df.drop('Group', axis=1)
        y = df['Group']

        print("STEP 3: Loading scaler + features...")

        scaler = joblib.load(os.path.join(BASE_DIR, 'ml_model', 'scaler.pkl'))
        feature_columns = joblib.load(os.path.join(BASE_DIR, 'ml_model', 'feature_columns.pkl'))

        print("STEP 4: Aligning columns...")
        X = X.reindex(columns=feature_columns, fill_value=0)

        print("STEP 5: Scaling...")
        X_scaled = scaler.transform(X)

        print("STEP 6: Loading models...")

        models = {
            "Logistic": joblib.load(os.path.join(BASE_DIR, 'ml_model', 'logistic.pkl')),
            "SVM": joblib.load(os.path.join(BASE_DIR, 'ml_model', 'svm.pkl')),
            "Random Forest": joblib.load(os.path.join(BASE_DIR, 'ml_model', 'random_forest.pkl')),
        }

        results = {}

        print("STEP 7: Predicting...")

        for name, model in models.items():
            y_pred = model.predict(X_scaled)
            acc = accuracy_score(y, y_pred)

            results[name] = {
                "accuracy": round(acc * 100, 2),
                "image": f"images/{name.lower().replace(' ', '_')}_cm.png"
            }

        context.update({
            "message": "Model Performance",
            "results": results,
            "heatmap_img": "images/heatmap.png"
        })

        return render(request, 'users/train.html', context)

    except Exception as e:
        print("ERROR:", str(e))
        return HttpResponse(f"Error: {str(e)}")




# Load model, scaler, features
model = joblib.load(os.path.join(BASE_DIR, 'ml_model', 'random_forest.pkl'))
scaler = joblib.load(os.path.join(BASE_DIR, 'ml_model', 'scaler.pkl'))
feature_columns = joblib.load(os.path.join(BASE_DIR, 'ml_model', 'feature_columns.pkl'))

def Prediction(request):
    prediction = None

    if request.method == 'POST':
        try:
            visit    = int(request.POST.get('visit'))
            mr_delay = int(request.POST.get('mr_delay'))
            age      = float(request.POST.get('age'))
            educ     = float(request.POST.get('educ'))
            ses      = float(request.POST.get('ses'))
            mmse     = float(request.POST.get('mmse'))
            cdr      = float(request.POST.get('cdr'))
            etiv     = float(request.POST.get('etiv'))
            nwbv     = float(request.POST.get('nwbv'))
            asf      = float(request.POST.get('asf'))
            gender   = request.POST.get('gender')

            input_dict = {
                'Visit':    visit,
                'MR Delay': mr_delay,
                'Age':      age,
                'EDUC':     educ,
                'SES':      ses,
                'MMSE':     mmse,
                'CDR':      cdr,
                'eTIV':     etiv,
                'nWBV':     nwbv,
                'ASF':      asf,
            }

            if 'M/F_M' in feature_columns:
                input_dict['M/F_M'] = 1 if gender == 'M' else 0

            input_df = pd.DataFrame([input_dict])
            input_df = input_df.reindex(columns=feature_columns, fill_value=0)
            input_scaled = scaler.transform(input_df)
            result = model.predict(input_scaled)[0]

            prediction_map = {0: "Nondemented", 1: "Demented", 2: "Converted"}
            prediction = prediction_map.get(result, str(result))

        except Exception as e:
            prediction = f"Error: {str(e)}"

    return render(request, 'users/predict.html', {'prediction': prediction})