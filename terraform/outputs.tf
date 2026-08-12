output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.app.id
}

output "public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.app.public_ip
}

output "public_dns" {
  description = "Public DNS of the EC2 instance"
  value       = aws_instance.app.public_dns
}

output "ssh_command" {
  description = "Command to SSH into the instance"
  value       = "ssh -i <PATH_TO_PRIVATE_KEY> ubuntu@${aws_instance.app.public_ip}"
}

output "application_url" {
  description = "URL to access the application"
  value       = "http://${aws_instance.app.public_ip}"
}
