# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[7.2].define(version: 2024_11_26_194110) do
  create_table "images", force: :cascade do |t|
    t.binary "image_data", null: false
    t.string "file_name", limit: 255, null: false
    t.integer "myotube_amount", null: false
    t.integer "project_id", null: false
    t.datetime "deleted_at"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["project_id"], name: "index_images_on_project_id"
  end

  create_table "myotubes", force: :cascade do |t|
    t.decimal "height", null: false
    t.decimal "width", null: false
    t.decimal "x_center", null: false
    t.decimal "y_center", null: false
    t.decimal "rotation", null: false
    t.decimal "confidence", null: false
    t.integer "type_class", null: false
    t.integer "image_id", null: false
    t.datetime "deleted_at"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["image_id"], name: "index_myotubes_on_image_id"
  end

  create_table "projects", force: :cascade do |t|
    t.string "name", limit: 100, null: false
    t.integer "myotube_count", null: false
    t.integer "picture_count", null: false
    t.datetime "start_date", null: false
    t.datetime "end_date", null: false
    t.datetime "deleted_at"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  add_foreign_key "images", "projects"
  add_foreign_key "myotubes", "images"
end
