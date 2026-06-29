# 📊 Database Models & Architecture

This document provides a technical overview of the data structures used in the Smart Cafe project.

## 🧱 Core Application Models

### `Staff`
Stores employee information and roles.
- **Roles**: Waiter, Chef, Admin, Cleaner.
- **Features**: SMS notification simulation via `send_sms()`.

### `Table`
Represents physical tables in the cafe.
- **Status**: Free, Occupied, Reserved, Cleaning.
- **Logic**: Handles table lifecycle (`occupy()`, `free_table()`, `mark_free()`).

### `Category` & `MenuItem`
The heart of the digital menu.
- **JSONField**: `serving_options` allows for flexible portion sizes (e.g., [0.5, 1.0, 1.5]).
- **Calculations**: `prep_time_display` property for human-readable time.
- **Features**: Weight, Calories, Vitamins, and "Popular" tags.

---

## 🛒 Orders Application Models

### `Order`
The primary transaction record.
- **Status Workflow**: Pending ➡️ Confirmed ➡️ Preparing ➡️ Ready ➡️ Delivered ➡️ Completed.
- **Methods**: `update_total()`, `complete_order()`.

### `OrderItem`
Line items within an order.
- **Calculation**: Automatically calculates `subtotal` on `save()` based on quantity and servings.

### `Payment`
Financial transaction tracking.
- **Methods**: Cash, Card, Click, Payme, Uzum.
- **Status**: Pending, Success, Failed, Refunded.

### `WaiterCall`
Real-time service signal.
- **Logic**: Tracks response time and staff replies.

---

## 💬 Feedback Application Models

### `Feedback`
Captures customer experience.
- **Rating**: 1 to 5 stars.
- **Anonymity**: Option for anonymous submissions.
- **Context**: Links back to the specific table.

---

## 🛠 Model Highlights
1. **Validation**: Use of `MinValueValidator` for quantities.
2. **Localization**: All `verbose_name` and `help_text` are in Uzbek.
3. **Efficiency**: Use of `ordering` Meta classes for consistent UI display.
4. **Extensibility**: `JSONField` usage demonstrates modern PostgreSQL/SQLite compatibility.
