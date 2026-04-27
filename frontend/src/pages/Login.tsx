import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
	const navigate = useNavigate();
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");

	const onSubmit = (e: FormEvent) => {
		e.preventDefault();
		if (email && password) {
			navigate("/dashboard");
		}
	};

	return (
		<div className="auth-wrap">
			<form className="card auth-card" onSubmit={onSubmit}>
				<h1>CloudSec Login</h1>
				<input
					type="email"
					placeholder="Email"
					value={email}
					onChange={(e) => setEmail(e.target.value)}
					required
				/>
				<input
					type="password"
					placeholder="Password"
					value={password}
					onChange={(e) => setPassword(e.target.value)}
					required
				/>
				<button type="submit">Sign In</button>
			</form>
		</div>
	);
}
