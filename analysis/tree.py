from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics 
from sklearn import tree
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


df = pd.read_csv('output/input.csv')
df_ae_hospital_discharge = df[df['ae_attendance_hosp_discharge']==1]



features = ['ae_attendance_hosp_discharge','risk_group', 'ae_attendance_covid_status', 'ae_attendance_respiratory_status', 'positive_covid_test_before_ae_attendance', 'positive_covid_test_month_before_ae_attendance', 'positive_covid_test_week_before_ae_attendance', 'covid_primary_care_before_ae_attendance', 'suspected_covid_primary_care_before_ae_attendance']

max_depths = np.linspace(1, 20, 20, endpoint=True)
min_samples_splits = np.linspace(0.1, 1, 10, endpoint=True)
min_samples_leaf = np.linspace(0.1, 0.5, 5, endpoint=True)

params = {
    "max_depth": max_depths,
    "min_samples_split": min_samples_splits,
    "min_samples_leaf": min_samples_leaf
}



X = pd.get_dummies(df[features],drop_first=False)
y = df['emergency_covid_hospital_admission'].notna().astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)

clf = GridSearchCV(estimator=DecisionTreeClassifier(), param_grid=params, scoring='f1')
clf.fit(X_train, y_train)


clf = DecisionTreeClassifier(max_depth=clf.best_params['max_depth'], min_samples_split=clf.best_params['min_samples_split'], min_samples_leaf=clf.best_params['min_samples_leaf'])


clf= clf.fit(X_train,y_train)
y_pred = clf.predict(X_test)


results_array = np.column_stack([y_test, y_pred])
results_df = pd.DataFrame(results_array, columns=['real', 'pred'])
results_df.to_csv('output/results_df.csv')


fig = plt.figure(figsize=(25,20))
_ = tree.plot_tree(clf, 
                   feature_names=X.columns,  
                   class_names=['0', '1'],
                   filled=True)

plt.savefig('output/tree.png')