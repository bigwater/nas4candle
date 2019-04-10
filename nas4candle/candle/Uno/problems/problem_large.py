from nas4candle.nasapi.benchmark import Problem
from nas4candle.candle.Uno.models.uno_mlp_large import create_structure

# We create our Problem object with the Problem class, you don't have to name your Problem object 'Problem' it can be any name you want. You can also define different problems in the same module.
Problem = Problem()

# You define the create structure function. This function will return an object following the Structure interface. You can also have kwargs arguments such as 'num_cells' for this function.
Problem.add_dim('create_structure', {
    'func': create_structure,
})

# You define the hyperparameters used to train your generated models during the search.
Problem.add_dim('hyperparameters', {
    'batch_size': 32,
    'num_epochs': 1,
})

# Just to print your problem, to test its definition and imports in the current python environment.
if __name__ == '__main__':
    print(Problem)
