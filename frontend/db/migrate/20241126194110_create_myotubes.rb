class CreateMyotubes < ActiveRecord::Migration[7.0]
  def change
    create_table :myotubes do |t|
      t.decimal :height, null: false
      t.decimal :width, null: false
      t.decimal :x_center, null: false
      t.decimal :y_center, null: false
      t.decimal :rotation, null: false
      t.decimal :confidence, null: false
      t.integer :type_class, null: false
      t.references :image, null: false, foreign_key: true
      t.datetime :deleted_at  # Nullable deleted_at column for soft deletes

      t.timestamps
    end
  end
end
