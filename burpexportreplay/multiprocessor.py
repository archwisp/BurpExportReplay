import multiprocessing, time, random

# Returns True if there are threads available after pruning. Otherwise, returns False.
def pruneJobs(jobs, threads):
    for job in jobs:
        if not job.is_alive():
            jobs.remove(job)
    
    if len(jobs) < threads:
        return True
        
    return False

def waitForJobs(jobs, threads):
    while True:
        if pruneJobs(jobs, threads):
            break

def runJobs(jobs_queue, threads = 0, throttle = 0):
    # print "[*] Spawning %s processs with %s threads and a throttle of %s seconds" % (len(jobs_queue), threads, throttle)
    running_jobs = []

    for job in jobs_queue:
        waitForJobs(running_jobs, threads)
        
        if throttle:
            time.sleep(throttle)
        
        job.start()
        running_jobs.append(job)
    
    # print "[*] All processs spawned."

# def doSomething(i):
    # print '... [*] Process %s starting' % (i)
    # sleep = random.randint(5,10)
    # print "... [*] Process %s sleeping for %s seconds" % (i, sleep)
    # time.sleep(sleep)
    # print "... [*] Process %s done" % (i)
    
# if __name__ == '__main__':
    # jobs_queue = [] 
    # for num in range(1, 10):
        # print "... [*] Appending job %s" % (num)
        # jobs_queue.append(multiprocessing.Process(target=doSomething, args=(num,)))
    
    # runJobs(jobs_queue, threads = 3)
    # print "[*] runJobs() returned"
