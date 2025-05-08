from app import webserver, log
from flask import request, jsonify, abort

import json

@webserver.before_request
def before_request():
    '''Function to handle requests before they are processed by the route handlers.'''
    if request.method == 'POST' and webserver.tasks_runner.shutdown_event.is_set():
        abort(503, description="Server is shutting down...")

# Example endpoint definition
@webserver.route('/api/post_endpoint', methods=['POST'])
def post_endpoint():
    '''Example endpoint to handle POST requests.'''
    if request.method == 'POST':
        # Assuming the request contains JSON data
        data = request.json
        print(f"got data in post {data}")

        # Process the received data
        # For demonstration purposes, just echoing back the received data
        response = {"message": "Received data successfully", "data": data}

        # Sending back a JSON response
        return jsonify(response)

    return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/api/jobs', methods=['GET'])
def get_jobs():
    '''Endpoint to get the list of jobs and their statuses.'''
    job_list = [{str(job_id): status} for job_id, status
                in webserver.tasks_runner.jobs_dict.items()]
    return jsonify({
        "status": "done",
        "data": job_list
    })

@webserver.route('/api/num_jobs', methods=['GET'])
def get_num_jobs():
    '''Endpoint to get the number of jobs in the queue.'''
    return jsonify({"status": "done", "data": len(webserver.tasks_runner.task_queue.qsize())})

@webserver.route('/api/graceful_shutdown', methods=['GET'])
def graceful_shutdown():
    '''Endpoint to gracefully shutdown the server.'''

    log.logger.info("Received request for graceful shutdown")

    webserver.tasks_runner.shutdown()
    if webserver.tasks_runner.is_queue_empty():
        return jsonify({"status": "done"})
    return jsonify({"status": "error", "data": "shutting own"})

@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_response(job_id):
    '''Endpoint to get the results of a job.'''

    log.logger.info(f"Received results request for job ID: {job_id}")

    print(f"JobID is {job_id}")

    job_id = int(job_id)

    if job_id not in webserver.tasks_runner.jobs_dict:
        return jsonify({"status": "error", 'reason': "Job ID not found"})

    if webserver.tasks_runner.jobs_dict[job_id] == "running":
        return jsonify({"status": "running"})

    with open (f"results/{job_id}.json", "r") as f:
        res = json.load(f)
        return jsonify({"status": "done", "data": res})

    # If not, return running status
    return jsonify({"status": 'NotImplemented'})

@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    '''Endpoint to handle requests for states mean.'''
    data = request.json
    
    log.logger.info(f"Got request for states mean: {data}")

    question = data["question"]

    submit_job_to_thread_pool("states_mean", question = question)

    return jsonify({"job_id": webserver.job_counter - 1})

@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    '''Endpoint to handle requests for state mean.'''
    data = request.json
    
    log.logger.info(f"Got request for state mean: {data}")

    question = data["question"]
    state = data["state"]

    submit_job_to_thread_pool("state_mean", state, question)

    return jsonify({"job_id": webserver.job_counter - 1})


@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    '''Endpoint to handle requests for the best 5 states.'''
    data = request.json
    question = data["question"]

    log.logger.info(f"Got request for best 5 states: {data}")

    submit_job_to_thread_pool("best5", question = question)

    return jsonify({"job_id": webserver.job_counter - 1})

@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    '''Endpoint to handle requests for the worst 5 states.'''
    data = request.json
    question = data["question"]

    log.logger.info(f"Got request for worst 5 states: {data}")

    submit_job_to_thread_pool("worst5", question = question)

    return jsonify({"job_id": webserver.job_counter - 1})

@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    '''Endpoint to handle requests for the global mean.'''
    data = request.json
    question = data["question"]

    log.logger.info(f"Got request for global mean: {data}")

    submit_job_to_thread_pool("global_mean", question = question)

    return jsonify({"job_id": webserver.job_counter - 1})

@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    '''Endpoint to handle requests for the difference from the mean.'''
    data = request.json
    question = data["question"]

    log.logger.info(f"Got request for difference from mean: {data}")

    submit_job_to_thread_pool("diff_from_mean", question = question)

    return jsonify({"job_id": webserver.job_counter - 1})

@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    '''Endpoint to handle requests for the difference from the mean for a specific state.'''
    data = request.json
    question = data["question"]
    state = data["state"]

    log.logger.info(f"Got request for state difference from mean: {data}")

    submit_job_to_thread_pool("state_diff_from_mean", state, question)

    return jsonify({"job_id": webserver.job_counter - 1})

@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    '''Endpoint to handle requests for the mean by category.'''
    data = request.json
    question = data["question"]

    log.logger.info(f"Got request for mean by category: {data}")

    submit_job_to_thread_pool("mean_by_category", question = question)

    return jsonify({"job_id": webserver.job_counter - 1})

@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    '''Endpoint to handle requests for the mean by category for a specific state.'''
    data = request.json
    question = data["question"]
    state = data["state"]

    log.logger.info(f"Got request for state mean by category: {data}")

    submit_job_to_thread_pool("state_mean_by_category", state, question)

    return jsonify({"job_id": webserver.job_counter - 1})

# You can check localhost in your browser to see what this displays
@webserver.route('/')
@webserver.route('/index')
def index():
    routes = get_defined_routes()
    msg = f"Hello, World!\n Interact with the webserver using one of the defined routes:\n"

    # Display each route as a separate HTML <p> tag
    paragraphs = ""
    for route in routes:
        paragraphs += f"<p>{route}</p>"

    msg += paragraphs
    return msg

def get_defined_routes():
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes

def submit_job_to_thread_pool(job_type, state = None, question = None):
    '''Function to submit a job to the thread pool.'''
    webserver.tasks_runner.jobs_dict[webserver.job_counter] = "running"

    data = {
        "question": question,
        "state": state
    }
    job = [webserver.job_counter, job_type, data]

    webserver.tasks_runner.add_task(job)

    webserver.job_counter += 1

