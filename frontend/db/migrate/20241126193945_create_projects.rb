class CreateProjects < ActiveRecord::Migration[7.0]
  def change
    create_table :projects do |t|
      t.string :name, limit: 100, null: false
      t.integer :myotube_count, null: false
      t.integer :picture_count, null: false
      t.datetime :start_date, null: false
      t.datetime :end_date, null: false
      t.datetime :deleted_at  # Nullable column for soft deletes

      t.timestamps  # Automatically adds created_at and updated_at
    end
  end
end
