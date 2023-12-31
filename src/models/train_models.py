import sys
# Agregamos la ruta al directorio principal 'banck_CHURN' al PYTHONPATH para luego poder acceder a los modulos con rutas absolutas.
sys.path.append(r'C:\Users\Pablo\Documents\GitHub\bank_CHURN')
import pandas as pd
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import auc, f1_score, precision_score, make_scorer, roc_curve, roc_auc_score, recall_score, accuracy_score
from sklearn.model_selection import train_test_split,GridSearchCV, cross_val_score
import joblib
from src.visualization_analysis.visualize import plot_model
X = pd.read_csv('https://raw.githubusercontent.com/psochando/bank_CHURN/main/DATA/processed/dataset_completo_predictoras.csv')
y = pd.read_csv('https://raw.githubusercontent.com/psochando/bank_CHURN/main/DATA/processed/dataset_completo_target.csv')



# Permite probar un modelo eliminando variables y así comparar los resultados
# Estableciendo plot = True, obtenemos la matriz de confusión y la curva ROC del modelo
def try_model_without(model, drop_cols = [], X = X, y = y, plot = False):
    
    X = X.drop(columns = drop_cols)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 42)
    
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', model)
    ]).fit(X_train, y_train)
    
    y_pred_train = pipeline.predict(X_train)
    y_pred = pipeline.predict(X_test)

    probabs_train = pipeline.predict_proba(X_train)
    fpr, tpr, threshold = roc_curve(y_train, probabs_train[:,1])
    roc_auc_train = auc(fpr, tpr)
    recall_train = recall_score(y_train, y_pred_train)
    # Imprimo el AUC y Recall del train para comparar con el test y ver si el modelo pudiera estar sobreajustado (en cualquier caso más tarde se someterá a validación cruzada)
    print(f'\nAUC del train: {roc_auc_train}')
    print(f'Recall del train: {recall_train}')
    
    print('\nMétricas del test:')
    probabs = pipeline.predict_proba(X_test)
    fpr, tpr, threshold = roc_curve(y_test, probabs[:,1])
    roc_auc = auc(fpr, tpr)
    print(f'AUC:{roc_auc}')
    f1 = f1_score(y_test, y_pred)
    print(f'f1 score: {f1}')
    acc = accuracy_score(y_test, y_pred)
    print(f'Accuracy: {acc}')
    precision = precision_score(y_test, y_pred)
    print(f'Precision: {precision}')
    recall = recall_score(y_test, y_pred)
    print(f'Recall: {recall}')
    
    if plot == True:
        plot_model(model, y_test, y_pred, fpr, tpr)
        

# Una vez hemos elegido un modelo para entrenarlo con todos los datos, lo pasamos como argumento de esta función, que devuelve las métricas principales obtenidas de una validación cruzada
# save = True guarda el modelo en la carpeta MODELS con el nombre que elijamos
def final_training(model, X = X, y = y, save = False, name = 'Model'):

    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', model)
    ]).fit(X, y)
    
    auc_cross = cross_val_score(pipeline, X, y, cv=5, scoring='roc_auc')
    recall_cross = cross_val_score(pipeline, X, y, cv=5, scoring='recall')
    
    if save == True:
        joblib.dump(pipeline, rf'C:\Users\Pablo\Documents\GitHub\bank_CHURN\MODELS\{name}')

    print(f'Recall de {name}: {recall_cross.mean()} \nAUC de {name}: {auc_cross.mean()}')


svc = SVC(C = 3, class_weight = 'balanced', degree = 3, kernel = 'poly', coef0 = 0.5, probability = True, random_state = 42)
svc1 = SVC(C = 0.1, class_weight = 'balanced', gamma = 10, kernel = 'rbf', probability = True, random_state = 42)

final_training(svc, save = False, name = 'SVC')  # Recall: 0.7520812256106375, AUC: 0.8543207822361568
final_training(svc1, save = False, name = 'SVC1')  # Recall: 0.8134484752131812, AUC: 0.8155395439141406