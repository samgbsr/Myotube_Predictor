class CreateImages < ActiveRecord::Migration[7.0]
  def change
    create_table :images do |t|
      t.binary :image_data, null: false  # Store binary image data
      t.string :file_name, limit: 255, null: false
      t.integer :myotube_amount, null: false
      t.references :project, null: false, foreign_key: true
      t.datetime :deleted_at  # Nullable deleted_at column for soft deletes

      t.timestamps
    end
  end
end
