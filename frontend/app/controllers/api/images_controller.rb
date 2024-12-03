# app/controllers/api/images_controller.rb
class Api::ImagesController < ApplicationController
    require 'net/http'
    require 'json'
    
    def create
      file = params[:image][:file_name]
      project_id = params[:image][:project_id]
    
      uri = URI.parse('http://localhost:5000/process-image')
      request = Net::HTTP::Post::Multipart.new(
        uri.path,
        "image" => UploadIO.new(file.tempfile, file.content_type, file.original_filename),
        "project_id" => project_id
      )
    
      response = Net::HTTP.start(uri.host, uri.port) do |http|
        http.request(request)
      end
    
      if response.is_a?(Net::HTTPSuccess)
        processed_image_data = response.body
        predictions = JSON.parse(response['predictions'])
    
        image = Image.create!(
          file_name: file.original_filename,
          project_id: project_id,
          myotube_amount: predictions.size,
          image_data: processed_image_data
        )
    
        predictions.each do |prediction|
          Myotube.create!(
            image_id: image.id,
            x_center: prediction['coords'][0],
            y_center: prediction['coords'][1],
            width: prediction['coords'][2],
            height: prediction['coords'][3],
            rotation: prediction['coords'][4],
            confidence: prediction['confidence'],
            type_class: prediction['class']
          )
        end
    
        project = Project.find(project_id)
        project.update!(myotube_count: project.images.sum(:myotube_amount))
    
        flash[:success] = 'Image uploaded and processed successfully!'
      else
        flash[:error] = 'Failed to process the image.'
      end
    
      redirect_to images_path
    end
    
    def show_image
        image = Image.find(params[:id])
        send_data image.image_data, type: 'image/png', disposition: 'inline'
      end
      
    
  end
  