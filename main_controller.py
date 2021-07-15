# Files

import optuna
from optuna import Trial

from backtest_runner import create_backtest_runner
from cli.print_utils import print_info


class MainController:

    @staticmethod
    async def run(args) -> None:
        async with create_backtest_runner(args) as runner:

            if args.alpha_hyperopt:
                study = optuna.create_study()

                def objective(trial: Trial):
                    return runner.run_hyperopt_iteration(trial)

                study.optimize(objective, n_trials=100)
                print_info(f"Best results {study.best_params}")
            else:
                runner.run_outputted_backtest()
