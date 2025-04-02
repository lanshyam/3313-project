#include <mysql_driver.h>
#include <mysql_connection.h>
#include <cppconn/prepared_statement.h>
#include <pistache/endpoint.h>
#include <pistache/router.h>
#include <iostream>
#include <mutex>
#include <json/json.h> // Install: `sudo apt-get install libjsoncpp-dev`

using namespace Pistache;
using namespace std;

// Database globals (simplified; use connection pooling in production)
sql::mysql::MySQL_Driver *driver;
sql::Connection *con;
mutex dbMutex;

// Connect to MySQL
void connectDB() {
    try {
        driver = sql::mysql::get_mysql_driver_instance();
        con = driver->connect("tcp://localhost:3306", "root", "Ans19122004");
        con->setSchema("budgets");
        cout << "Connected to MySQL!" << endl;
    } catch (sql::SQLException &e) {
        cerr << "MySQL Error: " << e.what() << endl;
        exit(1);
    }
}

// Add expense (ACID transaction)
string addExpense(int user_id, int category_id, float amount, const string &description) {
    lock_guard<mutex> lock(dbMutex);
    try {
        con->setAutoCommit(false); // Start transaction

        // Insert expense
        sql::PreparedStatement *pstmt = con->prepareStatement(
            "INSERT INTO Expenses (user_id, category_id, amount, description) VALUES (?, ?, ?, ?)"
        );
        pstmt->setInt(1, user_id);
        pstmt->setInt(2, category_id);
        pstmt->setDouble(3, amount);
        pstmt->setString(4, description);
        pstmt->executeUpdate();
        delete pstmt;

        con->commit(); // Commit if successful
        return "Expense added successfully!";
    } catch (sql::SQLException &e) {
        con->rollback(); // Rollback on error
        return "Error: " + string(e.what());
    }
}

// Get expenses by user (JSON response)
string getExpenses(int user_id) {
    lock_guard<mutex> lock(dbMutex);
    Json::Value root;
    Json::StreamWriterBuilder writer;

    try {
        sql::PreparedStatement *pstmt = con->prepareStatement(
            "SELECT category_id, amount, description FROM Expenses WHERE user_id = ?"
        );
        pstmt->setInt(1, user_id);
        sql::ResultSet *res = pstmt->executeQuery();

        while (res->next()) {
            Json::Value expense;
            expense["category"] = res->getInt("category_id");
            expense["amount"] = res->getDouble("amount");
            expense["description"] = res->getString("description");
            root.append(expense);
        }
        delete res;
        delete pstmt;
    } catch (sql::SQLException &e) {
        root["error"] = e.what();
    }

    return Json::writeString(writer, root);
}

// HTTP endpoint setup
void setupRoutes(Rest::Router &router) {
    Rest::Routes::Post(router, "/add_expense", Rest::Routes::bind([](const Rest::Request &request, Http::ResponseWriter response) {
        Json::Value reqBody;
        Json::CharReaderBuilder reader;
        string err;

        // Parse JSON
        if (!Json::parseFromStream(reader, request.body(), &reqBody, &err)) {
            response.send(Http::Code::Bad_Request, "Invalid JSON");
            return;
        }

        // Call addExpense()
        string result = addExpense(
            reqBody["user_id"].asInt(),
            reqBody["category_id"].asInt(),
            reqBody["amount"].asFloat(),
            reqBody["description"].asString()
        );

        response.send(Http::Code::Ok, result);
    }));

    Rest::Routes::Get(router, "/get_expenses/:user_id", Rest::Routes::bind([](const Rest::Request &request, Http::ResponseWriter response) {
        int user_id = stoi(request.param(":user_id").as<string>());
        response.send(Http::Code::Ok, getExpenses(user_id));
    }));
}

int main() {
    connectDB(); // Initialize MySQL

    // Start HTTP server
    Address addr(Ipv4::any(), Port(9080));
    auto opts = Http::Endpoint::options().threads(4); // Thread pool
    Http::Endpoint server(addr);
    server.init(opts);

    Rest::Router router;
    setupRoutes(router);
    server.setHandler(router.handler());
    server.serve();

    return 0;
}