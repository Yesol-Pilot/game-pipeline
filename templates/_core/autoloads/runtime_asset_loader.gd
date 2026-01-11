extends Node

# 런타임 에셋 로더 (Hot Swap)
# URL/로컬 경로에서 이미지 로드하여 Texture2D 반환

signal texture_loaded(url: String, texture: Texture2D)
signal load_failed(url: String)

func load_texture_from_url(url: String, target_node: Node_texture_callback_reciever = null) -> void:
    var http_request = HTTPRequest.new()
    add_child(http_request)
    http_request.request_completed.connect(self._http_request_completed.bind(url, http_request, target_node))
    
    var error = http_request.request(url)
    if error != OK:
        print("[AssetLoader] HTTP Request failed: ", error)
        load_failed.emit(url)
        http_request.queue_free()

func _http_request_completed(result, response_code, headers, body, url, http_request, target_node):
    if result != HTTPRequest.RESULT_SUCCESS:
        print("[AssetLoader] Download failed for: ", url)
        load_failed.emit(url)
    else:
        var image = Image.new()
        var error = image.load_png_from_buffer(body)
        if error != OK:
            error = image.load_jpg_from_buffer(body)
            
        if error != OK:
            print("[AssetLoader] Image parse failed")
            load_failed.emit(url)
        else:
            var texture = ImageTexture.create_from_image(image)
            print("[AssetLoader] Texture loaded from: ", url)
            texture_loaded.emit(url, texture)
            
            # 타겟 노드가 있고 set_texture 메서드나 texture 속성이 있으면 자동 적용
            if target_node and is_instance_valid(target_node):
                if target_node.has_method("set_texture"):
                    target_node.set_texture(texture)
                elif "texture" in target_node:
                    target_node.texture = texture
                    
    http_request.queue_free()

func load_local_texture(path: String) -> Texture2D:
    var image = Image.new()
    var error = image.load(path)
    if error != OK:
        print("[AssetLoader] Failed to load local image: ", path)
        return null
    return ImageTexture.create_from_image(image)
