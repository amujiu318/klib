# Kmanager Launcher

### Usage
```
launch.py run_train.py --set model transformer n_epochs 5 --sweep
```

Enter sweep parameters, separating the key and values by `:` and each individual values by `,`. Enter empty line to finish. Example:
```
Enter sweep parameters:
lr: 1e-3, 5e-4
batch_size: 32, 64, 128

```

Sample output (printing the python command):
```
python run_train.py --set lr 0.001 batch_size 32 model transformer n_epochs 5 exp lr_0.001_batch_size_32_model_transformer_n_epochs_5
python run_train.py --set lr 0.001 batch_size 64 model transformer n_epochs 5 exp lr_0.001_batch_size_64_model_transformer_n_epochs_5
python run_train.py --set lr 0.001 batch_size 128 model transformer n_epochs 5 exp lr_0.001_batch_size_128_model_transformer_n_epochs_5
python run_train.py --set lr 0.0005 batch_size 32 model transformer n_epochs 5 exp lr_0.0005_batch_size_32_model_transformer_n_epochs_5
python run_train.py --set lr 0.0005 batch_size 64 model transformer n_epochs 5 exp lr_0.0005_batch_size_64_model_transformer_n_epochs_5
python run_train.py --set lr 0.0005 batch_size 128 model transformer n_epochs 5 exp lr_0.0005_batch_size_128_model_transformer_n_epochs_5
```

Run the launch script anywhere by adding
```
alias klaunch={path to launch.py}
```
to `~/.bashrc`, then run
```
klaunch run_train.py --sweep
```

### To do
- Centralized experiment management
- Source code backup
- Slurm support
