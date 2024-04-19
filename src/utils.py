import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import KFold


def read_txt(path):
    """
    Read txt file of given path
    """
    with open(f"{path}", "r") as file:
        lines = file.readlines()
    res = []
    for line in lines:
        res.append(line.strip())
    return " ".join(res)


def kfold_cv_param_tuning(model_cls, params, df_train, k=5):
    res = {"idx": [], "score": []}

    for i, param in enumerate(params):
        model = model_cls(**param)
        kf = KFold(n_splits=k, shuffle=True, random_state=42)
        print(f"Training for param config {i}")
        for train_index, test_index in kf.split(df_train):
            model.fit(df_train.loc[train_index], df_train.loc[train_index].label)
            score = model.score(
                df_train.loc[test_index], df_train.loc[test_index].label
            )
            # record result
            res["idx"].append(i)
            res["score"].append(score)

    res_df = pd.DataFrame(res)

    sns.boxplot(x="idx", y="score", data=res_df)
    plt.show()

    opt_param_id = res_df.groupby("idx")["score"].mean().idxmax()
    print("Optimum param config:")
    for k, v in params[opt_param_id].items():
        print(f"{k} = {v}")

    return res_df[res_df.idx == opt_param_id]
