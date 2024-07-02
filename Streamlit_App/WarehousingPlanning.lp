\* WarehousingPlanning *\
Minimize
Sum_of_Transporting_Costs: 10 Route_Warehouse_1_Customer_1
 + 14 Route_Warehouse_1_Customer_2 + 20 Route_Warehouse_2_Customer_1
 + 15 Route_Warehouse_2_Customer_2
Subject To
Sum_of_Products_from_Warehouse_Warehouse_1: Route_Warehouse_1_Customer_1
 + Route_Warehouse_1_Customer_2 <= 200
Sum_of_Products_from_Warehouse_Warehouse_2: Route_Warehouse_2_Customer_1
 + Route_Warehouse_2_Customer_2 <= 150
Sum_of_Products_to_Customer_Customer_1: Route_Warehouse_1_Customer_1
 + Route_Warehouse_2_Customer_1 >= 300
Sum_of_Products_to_Customer_Customer_2: Route_Warehouse_1_Customer_2
 + Route_Warehouse_2_Customer_2 >= 50
Bounds
 0 <= Route_Warehouse_1_Customer_1
 0 <= Route_Warehouse_1_Customer_2
 0 <= Route_Warehouse_2_Customer_1
 0 <= Route_Warehouse_2_Customer_2
Generals
Route_Warehouse_1_Customer_1
Route_Warehouse_1_Customer_2
Route_Warehouse_2_Customer_1
Route_Warehouse_2_Customer_2
End
