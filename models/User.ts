import mongoose from 'mongoose';

const UserSchema = new mongoose.Schema({
  telegramId: { type: Number, required: true, unique: true },
  username: { type: String },
  firstName: { type: String },
  lastSeen: { type: Date, default: Date.now },
});

// On utilise mongoose.models pour éviter les erreurs de re-déclaration en mode développement
const User = mongoose.models.User || mongoose.model('User', UserSchema);

export default User;