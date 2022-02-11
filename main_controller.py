# Files
import os
import sys

import optuna
from optuna import Trial

from backtest_runner import create_backtest_runner
from cli.print_utils import print_info


class MainController:

    @staticmethod
    async def run(args, online: bool) -> None:
        async with create_backtest_runner(args, online) as runner:

            if args.alpha_hyperopt:
                os.environ["VERBOSITY"] = "no_warnings"
                study = optuna.create_study()

                if args.n_trials and args.n_trials > 0:
                    n_trials = args.n_trials
                else:
                    n_trials = 100

                print_info(f"Running parameter hyperoptimization with {n_trials} trials.")
                print_info("If you want to exit the program halfway, press 'ctrl + c', and you will get the "
                           "intermediate results.")

                def objective(trial: Trial):
                    return runner.run_hyperopt_iteration(trial)

                try:
                    study.optimize(objective, n_trials=n_trials)
                except KeyboardInterrupt:
                    print_info("Quitting hyperoptimization.")
                    try:
                        print_info(f"Best results: {study.best_params}")
                    except ValueError:
                        print_info("No trials completed yet. Results not available.")
                    sys.exit()
                print_info(f"Best results: {study.best_params}")
            else:
                runner.run_outputted_backtest()
