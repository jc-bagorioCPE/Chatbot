const express = require("express");
const mysql = require("mysql");
const cors = require("cors");
const bcrypt = require("bcryptjs");

const app = express();
app.use(express.json());
app.use(cors());

const db = mysql.createConnection({
    host: "localhost",
    user: "root",
    password: "",
    database: "register_db"
});

db.connect((err) => {
    if (err) {
        console.error("Database connection failed:", err);
        throw err;
    }
    console.log("MySQL Connected to register_db...");
});

app.post("/register", async (req, res) => {
    const { fullName, phoneNumber, email, birthdate, address, password } = req.body;

    if (!fullName || !phoneNumber || !email || !birthdate || !address || !password) {
        return res.status(400).json({ error: "All fields are required" });
    }

    const checkSql = "SELECT * FROM users WHERE phone_number = ? OR email = ?";
    db.query(checkSql, [phoneNumber, email], async (err, results) => {
        if (err) {
            console.error("Database error:", err);
            return res.status(500).json({ error: "Database error" });
        }
        if (results.length > 0) {
            return res.status(400).json({ error: "Phone number or email already registered" });
        }

        try {
            const hashedPassword = await bcrypt.hash(password, 10);

            const insertSql = "INSERT INTO users (full_name, phone_number, email, birthdate, address, password) VALUES (?, ?, ?, ?, ?, ?)";
            db.query(insertSql, [fullName, phoneNumber, email, birthdate, address, hashedPassword], (err, result) => {
                if (err) {
                    console.error("Insert error:", err);
                    return res.status(500).json({ error: "Registration failed" });
                }
                res.json({ success: true, message: "Registration successful" });
            });

        } catch (hashError) {
            console.error("Password hashing error:", hashError);
            return res.status(500).json({ error: "Internal server error" });
        }
    });
});

app.listen(5000, () => console.log("Server running on port 5000"));
