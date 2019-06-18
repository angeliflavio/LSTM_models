from selenium import webdriver
import time

driver = webdriver.Chrome()

# Hera predictive analytics tool
driver.get('http://heratools.app/workflow_prediction')

# once the browser is open, upload the json file 
# or create a flow manually

# list storing total times
times = []

# n simulations to test total time
for x in range(50):
    # click simulation and close results' window
    simulation_btn = driver.find_element_by_id('startSimulation')
    simulation_btn.click()
    time.sleep(1)
    # get total time
    total_time = driver.find_element_by_id('simulationTotalTime')
    print(x, '--', total_time.text)
    times.append(total_time.text)
#    if '372' in total_time.text:
#        break
    time.sleep(1)
    # exit from simulation results
    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element_with_offset(simulation_btn, 5, 5)
    action.click()
    action.perform()
    time.sleep(1)

# check all simulations
[print(x) for x in times]


