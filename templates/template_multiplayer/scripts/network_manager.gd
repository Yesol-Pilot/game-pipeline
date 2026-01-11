extends Node

# Multiplayer Network Manager

const PORT = 7000
const MAX_CLIENTS = 4

var peer = ENetMultiplayerPeer.new()
var player_scene = preload("res://templates/template_multiplayer/scenes/player_mp.tscn") # 동적 로드 가정

func host_game():
    var error = peer.create_server(PORT, MAX_CLIENTS)
    if error != OK:
        print("Failed to host: ", error)
        return
        
    multiplayer.multiplayer_peer = peer
    multiplayer.peer_connected.connect(_on_peer_connected)
    multiplayer.peer_disconnected.connect(_on_peer_disconnected)
    
    print("Hosting on port ", PORT)
    _spawn_player(1) # Host ID is always 1

func join_game(address: String = "localhost"):
    var error = peer.create_client(address, PORT)
    if error != OK:
        print("Failed to join: ", error)
        return
        
    multiplayer.multiplayer_peer = peer
    print("Joining ", address)

func _on_peer_connected(id: int):
    print("Peer connected: ", id)
    # 서버(Host)만 다른 플레이어들에게 새 플레이어를 스폰하라고 명령할 수 있음
    if multiplayer.is_server():
        _spawn_player(id)

func _on_peer_disconnected(id: int):
    print("Peer disconnected: ", id)
    if has_node(str(id)):
        get_node(str(id)).queue_free()

func _spawn_player(id: int):
    var player = player_scene.instantiate()
    player.name = str(id)
    add_child(player)
