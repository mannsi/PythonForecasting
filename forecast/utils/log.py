import logging

results_logger_name = "results_logger"

def init_file_and_console_logging(console_log_level, details_file_name, summary_file_name):
    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    details_file_handler = logging.FileHandler("{0}".format(details_file_name))
    details_file_handler.setFormatter(log_formatter)
    details_file_handler.setLevel(logging.INFO)
    root_logger.addHandler(details_file_handler)

    summary_file_handler = logging.FileHandler("{0}".format(summary_file_name))
    summary_file_handler.setFormatter(log_formatter)
    summary_file_handler.setLevel(logging.WARNING)
    root_logger.addHandler(summary_file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(console_log_level)
    root_logger.addHandler(console_handler)

    results_logger = logging.getLogger(results_logger_name)
    results_logger.setLevel(logging.INFO)
    results_logger_handler = logging.FileHandler("results_logger_diff_best_values.txt")
    results_logger_handler.setFormatter(logging.Formatter("%(message)s"))
    results_logger_handler.setLevel(logging.INFO)
    results_logger.addHandler(results_logger_handler)


def log_summary_for_item(item_id, results_for_item):
    logging.info("Results for {iid} in decreasing order".format(iid=item_id))
    for result in results_for_item:
        logging.info("Te:{te}, We:{we:.2f}. HN:{hn}, IN:{inp}".
                      format(te=result.training_error, we=result.weighted_error, hn=result.hidden_nodes,
                             inp=result.input_nodes))


def log_best_result_for_item(best_result, fp_weighted_errors, item_id):
    logging.warning("Best result for item {iid} by weighted error:")
    logging.warning(
        "== Result for {iid}. Best WE:{we:.2f}, FP_WE: {fp_we:.2f},  HN:{hn}, IN:{inp}, ByMonth:({by_month})"
            .format(we=best_result.weighted_error,
                   hn=best_result.hidden_nodes,
                   inp=best_result.input_nodes,
                   iid=item_id,
                   fp_we=fp_weighted_errors[best_result.item_id][0],
                   by_month=','.join('{:.2f}'.format(x) for x in best_result.errors_per_month)))

    results_logger = logging.getLogger(results_logger_name)
    results_logger.log(logging.INFO, "{iid}\t{fp_we:.2f}\t{NN_we:.2f}\t{hn}\t{inp}\t{NN_M1:.2f}\t{NN_M2:.2f}\t {NN_M3:.2f}\t {NN_M4:.2f}\t {NN_M5:.2f}\t {NN_M6:.2f}"
                       .format(fp_we=fp_weighted_errors[best_result.item_id][0],
                               NN_we=best_result.weighted_error,
                               iid=item_id,
                               hn=best_result.hidden_nodes,
                               inp=best_result.input_nodes,
                               NN_M1=best_result.errors_per_month[0],
                               NN_M2=best_result.errors_per_month[1],
                               NN_M3=best_result.errors_per_month[2],
                               NN_M4=best_result.errors_per_month[3],
                               NN_M5=best_result.errors_per_month[4],
                               NN_M6=best_result.errors_per_month[5]
                               ))
